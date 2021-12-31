from pytube import YouTube
from win32api import GetSystemMetrics
import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import requests
import os
from PIL import Image


class Video(YouTube):
    def __init__(self, video_url):
        super(Video).__init__()
        self.video_url = video_url
        self.video_main = YouTube(video_url)
        self.video_title = self.video_main.title
        self.video_preview = self.video_main.thumbnail_url
        self.video_author = self.video_main.author
        self.descr = self.video_main.description
        self.stream: str
        self.video: str

    def filter_video(self):
        # Да, пока все будет выглядеть именно так, потом что-нибудь придумаю
        # Yes, now it will look like this, maybe i'll think up how to upgrade this in the past
        self.video = self.video_main.streams.filter(res='1080p').\
            order_by('resolution').desc().first()
        return self.video

    def download(self, *path):
        self.video.download(*path)


class WarningMessage(QMessageBox):
    def __init__(self, title, message):
        QMessageBox.__init__(self)
        self.setText(f'{title}')
        self.setInformativeText(f"{message}")
        self.setIcon(QMessageBox.Critical)
        self.setStandardButtons(QMessageBox.Close)


class FileManager(QFileDialog):
    def __init__(self):
        super(FileManager).__init__()
        self.select_path_lay = QFileDialog.getExistingDirectory()


class Interface(QWidget, QColor, Video):
    def __init__(self):
        super().__init__()
        self.sys_width = GetSystemMetrics(0)
        self.sys_height = GetSystemMetrics(1)
        self.vid: object
        self.link_warn: object
        self.download_warn: object
        self.prepared_description: str
        self.edit = QLineEdit(self)
        self.edit.setGeometry(self.sys_width//4.5+20, 20, self.sys_width//5, self.sys_height//30)

        self.label_title = QLabel(self)
        self.label_title.setGeometry(self.sys_width//4.5+20, self.sys_height//15, self.sys_width//4, self.sys_height//30)
        self.label_title.setWordWrap(True)
        self.label_title.setMargin(2)
        self.label_title.setStyleSheet("background-color: lightgreen; border: 1px solid black;")

        self.label_author = QLabel(self)
        self.label_author.setGeometry(self.sys_width//4.5+20, self.sys_height//8, self.sys_width//4, self.sys_height//30)

        self.prev_label = QLabel(self)
        self.prev_label.setGeometry(20, 20, self.sys_width//5, self.sys_height//4)
        self.prev_label.setAlignment(Qt.AlignTop)
        #

        self.label_description = QLabel(self)
        self.label_description.setAlignment(Qt.AlignJustify)
        self.label_description.setMargin(2)
        self.label_description.setGeometry(20, self.sys_height//4+40, self.sys_width//5, self.sys_height//5)

        entry_button = QPushButton(self)
        entry_button.setText("Entry the link")
        entry_button.setGeometry(self.sys_width//2.25-10, 20, self.sys_width//20, self.sys_height//30)
        entry_button.setStyleSheet("background-color: lightgreen; border: 1px solid black;")
        entry_button.clicked.connect(self.create_video)

        def path_manage():
            self.filemanager = FileManager()
            path_label.setText("PATH: " + self.filemanager.select_path_lay)
            return self.filemanager

        path_button = QPushButton(self)
        path_button.setGeometry(self.sys_width//4.5+20, self.sys_height//3.5, self.sys_width//18, self.sys_height//15)
        path_button.setText("CHOOSE A PATH")
        path_button.clicked.connect(path_manage)

        path_label = QLabel(self)
        path_label.setGeometry(self.sys_width//3.5+20, self.sys_height//3.5, self.sys_width//5.3, self.sys_height//15)

        download_button = QPushButton(self)
        download_button.setGeometry(self.sys_width//3.65, self.sys_height//2.5,
                                    self.sys_width//6, self.sys_height//15)
        download_button.setText("DOWNLOAD!")
        download_button.clicked.connect(self.download_video)

        self.setGeometry(300, 300, self.sys_width // 2, self.sys_height // 2)
        self.setWindowTitle('TubeRobber')
        self.setStyleSheet("background-color: lightgray; border: 1px solid black")
        self.show()

    def cut_description(self):
        print(self.vid.descr)
        self.__interim_descr = list(self.vid.descr)
        for index, elem in enumerate(self.interim_descr):
            if index % self.sys_width//4/6.8 == 0:
                self.interim_descr.insert(index, '\n')
        self.prepared_description = ''.join(self.interim_descr)
        print(self.prepared_description)
        return self.prepared_description

    def get_preview(self):
        img_data = requests.get(self.vid.video_preview).content
        with open('clear_img.png', 'wb') as handler:
            handler.write(img_data)

    def __cut_preview(self):
        __img = Image.open('clear_img.png')
        cut_preview = __img.resize((self.sys_width//5, self.sys_height//4), Image.ANTIALIAS)
        cut_preview.save("cut_preview.png")

    def delete_preview(self):
        os.remove('clear_img.png')
        os.remove('cut_preview.png')

    def set_video_data(self):
        self.vid = Video(self.edit.text())
        self.label_title.setText(self.vid.video_title)
        self.label_description.setText(self.vid.descr)
        self.label_author.setText(self.vid.video_author)
        self.get_preview()
        self.__cut_preview()
        self.prev_label.setStyleSheet("background-image: url(cut_preview.png)")
        self.delete_preview()

    def create_video(self):
        try:
            self.set_video_data()
        except Exception:
            self.link_warn = WarningMessage("Something went wrong!...", "Please, check the link.")
            self.link_warn.show()

    def download_video(self):
        try:
            self.vid.filter_video()
            self.path = self.filemanager.select_path_lay
            self.vid.download(self.path)
        except Exception:
            self.download_warn = WarningMessage("Something went wrong!...", "Please, check the path, that you choices.")
            self.download_warn.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    interface = Interface()
    sys.exit(app.exec())
