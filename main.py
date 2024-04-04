import shutil
import datetime
from plyer import notification

def main():
    try:
        now = datetime.datetime.now()
        print("File copy test Strat")
        shutil.copy("tests/test.txt", f"tests/outputs/test_bkp_{now.date()}_{now.time().hour}_{now.time().minute}_{now.time().second}.txt")
        print("file copy test end")
        notification.notify(
            title="File backup test ended",
            message=f"File backup test successful at {now}",
            app_name='File_Backup'
        )

        print("folder copy test start")
        shutil.copytree("tests/test_tree", f"tests/outputs/test_tree_bkp_{now.date()}_{now.time().hour}_{now.time().minute}_{now.time().second}")
        print("folder copy test end")
        notification.notify(
            title="Folder backup test ended",
            message=f"Folder backup test successful at {now}",
            app_name='File_Backup'
        )
    except Exception as e:
        print(f"an exception has occured while copying the file {e}")

if __name__ == "__main__":
    main()