import shutil
import datetime
import os
from plyer import notification

class CopyController:
    def __init__(self, folder_header_name : str):
        self.folder_header_name = folder_header_name
        self.now = datetime.datetime.now()

    def file_copy(self, src: str, dest: str):
        try:  
            filename = os.path.basename(src)
            if not os.path.exists(os.path.join(dest, f"{self.folder_header_name}_{self.now.date()}_{self.now.time().hour}_{self.now.time().minute}_{self.now.time().second}")):
                os.makedirs(os.path.join(dest, f"{self.folder_header_name}_{self.now.date()}_{self.now.time().hour}_{self.now.time().minute}_{self.now.time().second}"))
            dest_path = os.path.join(dest, f"{self.folder_header_name}_{self.now.date()}_{self.now.time().hour}_{self.now.time().minute}_{self.now.time().second}", filename)
            shutil.copy(src, dest_path)
        except Exception as e:
            print(f"an exception has occured while copying the file {e}")

    def folder_copy(self, src: str, dest: str):
        try:
            folder_name = os.path.basename(src)
            dest_path = os.path.join(dest, f"{self.folder_header_name}_{self.now.date()}_{self.now.time().hour}_{self.now.time().minute}_{self.now.time().second}", folder_name)
            shutil.copytree(src, dest_path)
            
        except Exception as e:
            print(f"an exception has occured while copying the folder {e}")
    
    def notification(self,title: str,message: str):
        notification.notify(
                title=title,
                message=f"{message} at {datetime.datetime.now()}",
                app_name='File_Backup'
            )

