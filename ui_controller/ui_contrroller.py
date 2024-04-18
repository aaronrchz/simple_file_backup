from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

import os
from copy_controller.copy_controller import CopyController

class UiController:
    def __init__(self):
        Form, Window = uic.loadUiType("ui/file_backup.ui")
        self.app = QApplication([])
        self.window = Window()
        self.form = Form()
        self.form.setupUi(self.window)

        self.form.BrowseDestButton.clicked.connect(self.on_browse_dest_click)
        self.form.AddPathButton.clicked.connect(self.on_browse_add_click)
        self.form.AddPathButton.setEnabled(False)
        self.form.AddFileButton.clicked.connect(self.on_add_file_click)
        self.form.AddFileButton.setEnabled(False)
        self.form.TargetList.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.form.StartCopyButton.clicked.connect(self.on_start_click)
        self.form.StartCopyButton.setEnabled(False)
        self.form.DestinatioEdit.setText("")
        self.form.DestinatioEdit.setReadOnly(True)
    
    def start(self) :
        self.window.show()
        self.app.exec_()

    def on_browse_dest_click(self):
        folder_path = QFileDialog.getExistingDirectory(None, "Select Folder")
        if folder_path:
            self.form.DestinatioEdit.setText(folder_path)
            self.form.AddPathButton.setEnabled(True)
            self.form.AddFileButton.setEnabled(True)
            self.form.StatusLabel.setText("waiting for sources")

    def on_browse_add_click(self):
        folder_path = QFileDialog.getExistingDirectory(None, "Select Folder")
        if folder_path:
            self.form.TargetList.addItem(folder_path)
            self.form.StartCopyButton.setEnabled(True)
            self.form.StatusLabel.setText("ready")
            

    def on_add_file_click(self):
        file_paths, _ = QFileDialog.getOpenFileNames(None, "Select Files", "", "All Files (*)")
        if file_paths:
           for file_path in file_paths:
                self.form.TargetList.addItem(file_path)
                self.form.StartCopyButton.setEnabled(True)
                self.form.StatusLabel.setText("ready")
    
    def on_item_double_clicked(self, item):
        row = self.form.TargetList.row(item)
        self.form.TargetList.takeItem(row)
        if self.form.TargetList.count() == 0:
            self.form.StartCopyButton.setEnabled(False)
            self.form.StatusLabel.setText("waiting for sources")
    
    def on_start_click(self):
        try:
            self.form.BrowseDestButton.setEnabled(False)
            self.form.AddPathButton.setEnabled(False)
            self.form.AddFileButton.setEnabled(False)
            self.form.StartCopyButton.setEnabled(False)
            self.form.TargetList.setEnabled(False)
            self.form.progressBar.setValue(0)
            self.form.progressBar.setMinimum(0)
            copy_controller = CopyController('test_bkp')
            portion = 1 / self.form.TargetList.count();
            portion = int(portion * 1000)
            self.form.progressBar.setMaximum(portion * self.form.TargetList.count())
            currentval = 0
            for index in range(self.form.TargetList.count()):
                item = self.form.TargetList.item(index)
                self.form.StatusLabel.setText(f"Copying: {item.text()}")
                if os.path.isfile(item.text()):
                    copy_controller.file_copy(item.text(), self.form.DestinatioEdit.text())
                elif os.path.isdir(item.text()):
                    copy_controller.folder_copy(item.text(), self.form.DestinatioEdit.text())
                self.form.progressBar.setValue(index)
                currentval += portion
                self.form.progressBar.setValue(currentval)
            self.form.BrowseDestButton.setEnabled(True)
            self.form.AddPathButton.setEnabled(True)
            self.form.AddFileButton.setEnabled(True)
            self.form.StartCopyButton.setEnabled(True)
            self.form.TargetList.setEnabled(True)
            self.form.StatusLabel.setText("Done!")
        except Exception as e:
            self.form.StatusLabel.setText("Error!")
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText(str(e))
            msgBox.setWindowTitle("Error while copying")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            self.form.BrowseDestButton.setEnabled(True)
            self.form.AddPathButton.setEnabled(True)
            self.form.AddFileButton.setEnabled(True)
            self.form.StartCopyButton.setEnabled(True)
            self.form.TargetList.setEnabled(True)

                
            

