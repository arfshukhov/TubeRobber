# ver. 1.0.1.
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
        self.video: object

    def filter_video(self, resolution):
        # Да, пока все будет выглядеть именно так, потом что-нибудь придумаю
        # Yes, now it will look like this, maybe i'll think up how to upgrade this in the past
        self.video = self.video_main.streams.filter(res=str(resolution)). \
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
        self.set_res: object
        self.resolution: str
        self.link_warn: object
        self.download_warn: object
        self.prepared_description: str
        self.edit = QLineEdit(self)
        self.edit.setGeometry(self.sys_width // 4.5 + 20, 20, self.sys_width // 5, self.sys_height // 30)

        self.label_title = QLabel(self)
        self.label_title.setGeometry(self.sys_width // 4.5 + 20, self.sys_height // 15, self.sys_width // 4,
                                     self.sys_height // 30)
        self.label_title.setWordWrap(True)
        self.label_title.setMargin(2)
        self.label_title.setStyleSheet("background-color: lightgreen; border: 1px solid black;")

        self.label_author = QLabel(self)
        self.label_author.setGeometry(self.sys_width // 4.5 + 20, self.sys_height // 8, self.sys_width // 4,
                                      self.sys_height // 30)

        self.prev_label = QLabel(self)
        self.prev_label.setGeometry(20, 20, self.sys_width // 5, self.sys_height // 4)
        self.prev_label.setAlignment(Qt.AlignTop)
        #

        self.label_description = QLabel(self)
        self.label_description.setAlignment(Qt.AlignJustify)
        self.label_description.setMargin(2)
        self.label_description.setGeometry(20, self.sys_height // 4 + 40, self.sys_width // 5, self.sys_height // 5)

        entry_button = QPushButton(self)
        entry_button.setText("Entry the link")
        entry_button.setGeometry(self.sys_width // 2.25 - 10, 20, self.sys_width // 20, self.sys_height // 30)
        entry_button.setStyleSheet("background-color: lightgreen; border: 1px solid black;")
        entry_button.clicked.connect(self.create_video)

        path_button = QPushButton(self)
        path_button.setGeometry(self.sys_width // 4.5 + 20, self.sys_height // 3.5, self.sys_width // 18,
                                self.sys_height // 15)
        path_button.setText("CHOOSE A PATH")
        path_button.clicked.connect(self.path_manage)

        self.path_label = QLabel(self)
        self.path_label.setGeometry(self.sys_width // 3.5 + 20, self.sys_height // 3.5, self.sys_width // 5.3,
                                    self.sys_height // 15)

        self.res_label = QLabel(self)
        self.res_label.setGeometry(self.sys_width // 3.5 + 20, self.sys_height // 5.25, self.sys_width // 5.3,
                                   self.sys_height // 15)

        self.hd_button = QPushButton(self)
        self.hd_button.setGeometry(self.sys_width // 4.5 + 20, self.sys_height // 5.25, self.sys_width // 18,
                                   self.sys_height // 45)
        self.hd_button.setText("HD")
        self.hd_button.clicked.connect(self.set_hd_res)

        self.fullhd_button = QPushButton(self)
        self.fullhd_button.setGeometry(self.sys_width // 4.5 + 20, self.sys_height // 5.25 + self.sys_height // 45,
                                       self.sys_width // 18, self.sys_height // 45)
        self.fullhd_button.setText("FULL HD")
        self.fullhd_button.clicked.connect(self.set_fullhd_res)

        self.uhd_button = QPushButton(self)
        self.uhd_button.setGeometry(self.sys_width // 4.5 + 20, self.sys_height // 5.25 + self.sys_height // 45 * 2,
                                    self.sys_width // 18, self.sys_height // 45)
        self.uhd_button.setText("UHD/4K")
        self.uhd_button.clicked.connect(self.set_uhd_res)

        download_button = QPushButton(self)
        download_button.setGeometry(self.sys_width // 3.65, self.sys_height // 2.5,
                                    self.sys_width // 6, self.sys_height // 15)
        download_button.setText("DOWNLOAD!")
        download_button.clicked.connect(self.download_video)

        self.setGeometry(300, 300, self.sys_width // 2, self.sys_height // 2)
        self.setWindowTitle('TubeRobber')
        self.setStyleSheet("background-color: lightgray; border: 1px solid black")
        self.show()

    def path_manage(self):
        self.filemanager = FileManager()
        self.path_label.setText("PATH: " + self.filemanager.select_path_lay)
        return self.filemanager

    # This method should align the text of the video description,
    # but I messed up with the algorithm.
    def cut_description(self):
        print(self.vid.descr)
        self.__interim_descr = list(self.vid.descr)
        for index, elem in enumerate(self.__interim_descr):
            if index % self.sys_width // 4 / 6.8 == 0:
                self.__interim_descr.insert(index, '\n')
        self.prepared_description = ''.join(self.__interim_descr)
        print(self.prepared_description)
        return self.prepared_description

    # This method requests a preview of the video
    def get_preview(self):
        img_data = requests.get(self.vid.video_preview).content
        with open('clear_img.png', 'wb') as handler:
            handler.write(img_data)

    def __cut_preview(self):
        __img = Image.open('clear_img.png')
        cut_preview = __img.resize((self.sys_width // 5, self.sys_height // 4), Image.ANTIALIAS)
        cut_preview.save("cut_preview.png")

    # This method removes both the scaled image
    # and the draft image so as not to leave file garbage.
    # Этот метод удаляет как отмасштабированное изображение,
    # так и черновое, чтобы не оставлять  файлового мусора.
    def delete_preview(self):
        os.remove('clear_img.png')
        os.remove('cut_preview.png')

    # This method collects all the data in a heap
    # and creates an instance of the Video class.

    def set_video_data(self):
        self.vid = Video(self.edit.text())
        self.label_title.setText(self.vid.video_title)
        self.label_description.setText(self.vid.descr)
        self.label_author.setText(self.vid.video_author)
        self.get_preview()
        self.__cut_preview()
        self.prev_label.setStyleSheet("background-image: url(cut_preview.png)")
        self.delete_preview()

    # These three methods set the value for the self.resolution attribute,
    # as well as for the label showing the selected resolution.
    def set_hd_res(self):
        self.res_label.setText("HD 720p")
        self.resolution = "720p"
        return self.resolution

    def set_fullhd_res(self):
        self.res_label.setText("FULL HD 1080p")
        self.resolution = "1080p"
        return self.resolution

    def set_uhd_res(self):
        self.res_label.setText("ULTRA HD 4K 2160p")
        self.resolution = "2160p"
        return self.resolution

    # This method tries to call the set_video_data method,
    # and if something goes wrong, throws an exception.
    # Этот метод пробует вызвать метод set_video_data,
    # а если что-то идет не так, выдает исключение.
    def create_video(self):
        try:
            self.set_video_data()
        except Exception:
            self.link_warn = WarningMessage("Something went wrong!...", "Please, check the link.")
            self.link_warn.show()

    def download_video(self):
        try:
            self.vid.filter_video(self.resolution)
            self.path = self.filemanager.select_path_lay
            self.vid.download(self.path)
        except Exception:
            self.download_warn = WarningMessage("Something went wrong!...", "Please, check the path, that you choices\
            or resolution.")
            self.download_warn.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    interface = Interface()
    sys.exit(app.exec())
