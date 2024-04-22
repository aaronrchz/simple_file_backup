from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QPoint
from PyQt5.QtGui import QIcon, QPixmap

import os
import json
from datetime import datetime

from copy_controller.copy_controller import CopyController
from ui.style_sheet import Styles

class _themes:
    dark = 0
    light = 1

class CopyThread(QThread):
    update_progress = pyqtSignal(int, str) 
    finished = pyqtSignal() 

    def __init__(self, target_list, destination, parent=None):
        super(CopyThread, self).__init__(parent)
        self.target_list = target_list
        self.destination = destination
        self.copy_controller = CopyController('bkp')

    def run(self):
        portion = 1 / len(self.target_list)
        portion = int(portion * 1000)
        currentval = 0
        for index, item_path in enumerate(self.target_list):
            self.update_progress.emit(currentval, f"Copying: {item_path}")
            if os.path.isfile(item_path):
                self.copy_controller.file_copy(item_path, self.destination)
            elif os.path.isdir(item_path):
                self.copy_controller.folder_copy(item_path, self.destination)
            currentval += portion
            self.update_progress.emit(currentval, f"Copying: {item_path}")
        self.update_progress.emit(currentval, f"Copying: {item_path}")
        self.finished.emit()

class UiController:
    def __init__(self):
        Form, Window = uic.loadUiType("ui/file_backup.ui")
        self.app = QApplication([])
        self.app.setStyleSheet(Styles.Dark)
        self.window = Window()
        self.form = Form()
        self.form.setupUi(self.window)
        #self.window.setFixedSize(self.window.size())
        self.window.setWindowFlags(Qt.FramelessWindowHint)
        self.window.setWindowIcon(QIcon("ui/icons/simple_file_backup.ico"))
        self.window.setWindowTitle("Simple File Backup")

        self.form.BrowseDestButton.clicked.connect(self._on_browse_dest_click)
        self.form.AddPathButton.clicked.connect(self._on_browse_add_click)
        self.form.AddFileButton.clicked.connect(self._on_add_file_click)
        self.form.TargetList.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.form.StartCopyButton.clicked.connect(self._on_start_click)
        self.form.ThemeButton.clicked.connect(self._on_theme_button_click)
        self.form.InfoButton.clicked.connect(self._show_about_message)
        self.form.ExitPushButton.clicked.connect(lambda: self.app.exit())
        self.form.MinimizePushButton.clicked.connect(lambda: self.window.repaint() or self.window.showMinimized())
        self.window.clickPosition = QPoint()
        self.window.mousePressEvent = self._on_mouse_press
        self.form.CustomtitleBar.mouseMoveEvent = self._on_mouse_move
        self.form.CancelButton.hide()

        self.main_icon  = QPixmap('ui/icons/simple_file_backup.ico')
        self.form.IconL.setPixmap(self.main_icon.scaled(31, 21, Qt.KeepAspectRatio))

        self.jsonStructure = {
            'destination': '',
            'source_list': [],
            'last_backup': '',
            'theme': 'dark',
            'first_run': True
        }
        self.defaultjsonStructure = self.jsonStructure

        config_result  = self._config_loader()
        if not config_result:
            self._set_defualt_config()
    
    def start(self ) :
        self.window.show()
        self.app.exec_()

    def _on_mouse_move(self, event):
        if self.window.isMaximized() == False:
            self.window.move(self.window.pos() + event.globalPos() - self.window.clickPosition)
            self.window.clickPosition = event.globalPos()
            event.accept()

    def _on_mouse_press(self, event):
        self.window.clickPosition = event.globalPos()
        pass


    def _on_browse_dest_click(self):
        folder_path = QFileDialog.getExistingDirectory(None, "Select Folder")
        if folder_path:
            self.form.DestinatioEdit.setText(folder_path)
            self.jsonStructure['destination'] = folder_path
            self._write_config()
            self.form.AddPathButton.setEnabled(True)
            self.form.AddFileButton.setEnabled(True)
            self.form.StatusLabel.setText("waiting for sources")

    def _on_browse_add_click(self):
        folder_path = QFileDialog.getExistingDirectory(None, "Select Folder")
        if folder_path:
            self.jsonStructure['source_list'].append(folder_path)
            self._write_config()
            self.form.TargetList.addItem(folder_path)
            self.form.StartCopyButton.setEnabled(True)
            self.form.StatusLabel.setText("ready")
            

    def _on_add_file_click(self):
        file_paths, _ = QFileDialog.getOpenFileNames(None, "Select Files", "", "All Files (*)")
        if file_paths:
           for file_path in file_paths:
                self.jsonStructure['source_list'].append(file_path)
                self._write_config()
                self.form.TargetList.addItem(file_path)
                self.form.StartCopyButton.setEnabled(True)
                self.form.StatusLabel.setText("ready")
    
    def _on_item_double_clicked(self, item):
        row = self.form.TargetList.row(item)
        self.form.TargetList.takeItem(row)
        self.jsonStructure['source_list'].pop(row)
        self._write_config()
        
        if self.form.TargetList.count() == 0:
            self.form.StartCopyButton.setEnabled(False)
            self.form.StatusLabel.setText("esperando por fuentes")
    
    def _on_start_click(self):
        if self.jsonStructure['first_run']:
            self.jsonStructure['first_run'] = False
            self._write_config()
            self._show_about_message()
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QIcon(self.main_icon))
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("Once the copy process Starts, the UI will be frozen until the process is finished, and IT CANNOT BE STOPPED UNLESS YOU FORCE IT, it is recommended to ovid copying files bigger than 500Mb. Do you still want to continue?")
        msgBox.setWindowTitle("Warning")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        result = msgBox.exec_() 
        if result == QMessageBox.Ok:
            self._on_start_accept_click()

    def _on_start_accept_click(self):
        try:
            self._disable_ui_elements() 
            self.form.progressBar.setValue(0)
            self.form.progressBar.setMinimum(0)
            

            target_list = [self.form.TargetList.item(index).text() for index in range(self.form.TargetList.count())]
            destination = self.form.DestinatioEdit.text()
            portion = 1 / len(target_list)
            portion = int(portion * 1000)
            self.form.progressBar.setMaximum(portion * len(target_list))
            self.copy_thread = CopyThread(target_list, destination)
            self.copy_thread.update_progress.connect(self._update_progress_ui)
            self.copy_thread.finished.connect(self._copy_finished)
            self.jsonStructure['last_backup'] = str(datetime.now())
            self.form.LastBackupLabel.setText(self.jsonStructure['last_backup'])
            self._write_config()
            self.copy_thread.start()
        except Exception as e:
            self._enable_ui_elements() 
            self.form.StatusLabel.setText("Error!")
            self._show_error_message(str(e))

    def _disable_ui_elements(self):
        self.form.BrowseDestButton.setEnabled(False)
        self.form.AddPathButton.setEnabled(False)
        self.form.AddFileButton.setEnabled(False)
        self.form.StartCopyButton.setEnabled(False)
        self.form.TargetList.setEnabled(False)

    def _enable_ui_elements(self):
        self.form.BrowseDestButton.setEnabled(True)
        self.form.AddPathButton.setEnabled(True)
        self.form.AddFileButton.setEnabled(True)
        self.form.StartCopyButton.setEnabled(True)
        self.form.TargetList.setEnabled(True)

    def _update_progress_ui(self, value, status):
        self.form.progressBar.setValue(value)
        self.form.StatusLabel.setText(status)

    def _copy_finished(self):
        self._enable_ui_elements()
        self.form.StatusLabel.setText("Done!")

    def _show_error_message(self, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText(message)
        msgBox.setWindowTitle("Error while copying")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def _show_about_message(self):
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QIcon(self.main_icon))
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Simple File Backup is a simple, free, open-source tool for backing up files and folders. You can find the source code at https://github.com/aaronrchz/simple_file_backup.\n\nLegal Notice: This software is provided 'as is', without any kind of warranty, expressed or implied. Use of this software is at your own risk. The author is not responsible for any data loss, damage, or any other liabilities that may arise from the use or inability to use this software. It is recommended to back up responsibly and verify backups regularly.")
        msgBox.setWindowTitle("About")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def _config_loader(self):
        config_file_name = 'config.json'
        
        if not os.path.exists(config_file_name):
            self._write_config()
            return False
        else:
            with open(config_file_name, 'r') as f:
                config = json.load(f)
                self.jsonStructure = config
                if config['theme'] == 'dark':
                    self.themeflag = _themes.dark
                    self._set_theme()
                else:
                    self.themeflag = _themes.light
                    self._set_theme()
                if config['destination'] != "":
                    self.form.AddPathButton.setEnabled(True)
                    self.form.AddFileButton.setEnabled(True)
                    self.form.DestinatioEdit.setText(config['destination'])
                    self.form.StatusLabel.setText("waiting for sources")
                    self.form.LastBackupLabel.setText(config['last_backup'])
                for source in config['source_list']:
                    self.form.TargetList.addItem(source)
                    self.form.StartCopyButton.setEnabled(True)
                    self.form.StatusLabel.setText("ready")
            return True
    
    def _write_config(self):
        with open('config.json', 'w') as f:
            json.dump(self.jsonStructure, f, indent=4)
    
    def _on_theme_button_click(self):
        if self.themeflag == _themes.dark:
            self.themeflag = _themes.light
            self._set_theme()
        elif self.themeflag == _themes.light:
            self.themeflag = _themes.dark
            self._set_theme()

    def _set_theme(self):
        if self.themeflag == _themes.light:
            self.jsonStructure['theme'] = 'light'
            self._write_config()
            self.form.ThemeButton.setIcon(QIcon('ui/icons/dark_theme.ico'))
            self.form.ExitPushButton.setIcon(QIcon('ui/icons/light/close.ico'))
            self.form.MinimizePushButton.setIcon(QIcon('ui/icons/light/minimize.ico'))
            self.form.InfoButton.setIcon(QIcon('ui/icons/light/info.ico'))
            self.app.setStyleSheet(Styles.Light)
        elif self.themeflag == _themes.dark:
            self.jsonStructure['theme'] = 'dark'
            self._write_config()
            self.form.ThemeButton.setIcon(QIcon('ui/icons/light_theme.ico'))
            self.form.ExitPushButton.setIcon(QIcon('ui/icons/dark/close.ico'))
            self.form.MinimizePushButton.setIcon(QIcon('ui/icons/dark/minimize.ico')) 
            self.form.InfoButton.setIcon(QIcon('ui/icons/dark/info.ico'))           
            self.app.setStyleSheet(Styles.Dark)
            self.themeflag = _themes.dark

    def _set_defualt_config(self):
        self.jsonStructure = self.defaultjsonStructure
        self._write_config()
        self.form.AddPathButton.setEnabled(False)
        self.form.AddFileButton.setEnabled(False)
        self.form.StartCopyButton.setEnabled(False)
        self.form.DestinatioEdit.setText("")
        self.form.DestinatioEdit.setReadOnly(True)
        self.themeflag = _themes.dark
        self._set_theme()
