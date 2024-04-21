# ![Logo](https://i.imgur.com/tB8QqJV.png) Simple file backup v0.0

This project aims to be a simple program to backup / copy your files and folders in batch, to a specified location.

This project is not intended to be a profesional backup software, it is a simple script that can be used periodically to copy the same files only by clicking a button.

## Warning

As this software aims to be used to backup files, it is importat to know that the author is not responsable for any data loss or corruption that may occur.

It is better and safer to have multiple backups of your files managed manually.


USE IT AT YOUR OWN RISK

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Compilation

This project is written in python so ideally you can download the source code and run it on a python3 enviromet with the dependencies installed.

If you want to compile the project you can use pyinstaller to create a standalone executable.

### Dependencies
- Python 3.11.4 or later
- PyQt5 : Used to create the GUI
- shutil : Used to copy files and folders

## Usage

![Screenshot](https://i.imgur.com/hBj3p73.png)

First you can add a destination path by writing it manually in the text box on top of the window, or by clicking the "Browse" button and selecting the path from the file explorer.

Then you can add the files and folders to backup by clicking the "Add File" or "Add Path" button and selecting the files and folders from the file explorer.

Finally, you can start the backup process by clicking the "Start backup" button.

The copying proccess cannot be stopped once it has started, but you can close the program to stop the proccess, however it is not recommended.



