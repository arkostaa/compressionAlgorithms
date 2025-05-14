import zipfile
import os
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from design import Ui_Dialog
from huffman_coding import compress as huffman_compress, decompress as huffman_decompress
from lz77 import lz77_compress, lz77_decompress_from_sequence
from deflate import deflate_compress, deflate_decompress
from BrotliComp import brotli_compress, brotli_decompress
import time


class MainWindow(QtWidgets.QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.selected_zip_file = None
        self.selected_files_for_zip = None
        self.selected_file_for_huffman_decompress = None
        self.selected_file_for_deflate = None
        self.selected_file_for_deflate_decompress = None
        self.selected_file_for_brotli = None
        self.selected_file_for_brotli_decompress = None
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowFlags(
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )

        self.connect_signals()

    def connect_signals(self):
        self.ui.chooseFile.clicked.connect(self.select_file_for_huffman)
        self.ui.ButtonEnter.clicked.connect(self.compress_with_huffman)

        self.ui.button_files_4.clicked.connect(self.select_file_for_huffman_decompress)
        self.ui.button_decompress.clicked.connect(self.decompress_with_huffman)

        self.ui.pushButton.clicked.connect(self.compress_with_lz77)
        self.ui.pushButton_2.clicked.connect(self.decompress_with_lz77)

        self.ui.chooseFile_3.clicked.connect(self.select_file_for_deflate)
        self.ui.pushButton_5.clicked.connect(self.compress_with_deflate)

        self.ui.button_files_5.clicked.connect(self.select_file_for_deflate_decompress)
        self.ui.button_decompress_2.clicked.connect(self.decompress_with_deflate)

        self.ui.ChooseFileBrotli.clicked.connect(self.select_file_for_brotli)
        self.ui.ButtonEnterBrotli.clicked.connect(self.compress_with_brotli)

        self.ui.ChooseFilesBrotli.clicked.connect(self.select_file_for_brotli_decompress)
        self.ui.buttonDecompBrotli.clicked.connect(self.decompress_with_brotli)

    def show_error_message(self, title, text, icon):
        """Вспомогательная функция для отображения стилизованных сообщений об ошибках."""
        msg = QMessageBox(self)
        msg.setStyleSheet("""
            QMessageBox QLabel { color: rgb(255, 255, 255); }
            QMessageBox { background-color: rgb(0, 0, 0); }
            QPushButton { 
                color: rgb(201, 216, 197); 
                background-color: rgb(70, 83, 66); 
                border-radius: 5px; 
                padding: 3px 5px; 
            }
            QPushButton:hover { background-color: rgb(71, 85, 67); }
            QPushButton:pressed { background-color: rgb(52, 62, 49); }
        """)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)
        msg.exec_()

    # ========== ZIP функционал ==========
    def select_files_for_zip(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите файлы для архивации", "", "Все файлы (*)")
        if files:
            self.ui.uploaded_files_2.setText(", ".join([os.path.basename(f) for f in files]))
            self.selected_files_for_zip = files
            self.ui.status_2.setText("Файлы выбраны")
        else:
            self.ui.status_2.setText("Файлы не выбраны")

    def compress_to_zip(self):
        if not hasattr(self, 'selected_files_for_zip'):
            self.show_error_message("Ошибка", "Сначала выберите файлы!", QMessageBox.Warning)
            return

        output_file, _ = QFileDialog.getSaveFileName(self, "Сохранить ZIP архив", "", "ZIP Archives (*.zip)")
        if output_file:
            try:
                with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file in self.selected_files_for_zip:
                        zipf.write(file, os.path.basename(file))
                self.ui.status_2.setText(f"Архив создан: {os.path.basename(output_file)}")
            except Exception as e:
                self.show_error_message("Ошибка", f"Ошибка при создании архива: {str(e)}", QMessageBox.Critical)

    def select_zip_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите ZIP архив", "", "ZIP Archives (*.zip)")
        if file:
            self.ui.uploaded_files_3.setText(os.path.basename(file))
            self.selected_zip_file = file
            self.ui.status_3.setText("Архив выбран")
        else:
            self.ui.status_3.setText("Архив не выбран")

    def decompress_zip(self):
        if not hasattr(self, 'selected_zip_file'):
            self.show_error_message("Ошибка", "Сначала выберите архив!", QMessageBox.Warning)
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Выберите папку для распаковки")
        if output_dir:
            try:
                with zipfile.ZipFile(self.selected_zip_file, 'r') as zipf:
                    zipf.extractall(output_dir)
                self.ui.status_3.setText(f"Архив распакован в: {output_dir}")
            except Exception as e:
                self.show_error_message("Ошибка", f"Ошибка при распаковке архива: {str(e)}", QMessageBox.Critical)

    # ========== Хаффман функционал ==========
    def select_file_for_huffman(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите файл для сжатия", "", "Текстовые файлы (*.txt)")
        if file:
            self.ui.chosenFile.setText(os.path.basename(file))
            self.selected_file_for_huffman = file
            self.ui.status.setText("Файл выбран")
            self.ui.origHuffmanText.clear()
        else:
            self.ui.status.setText("Файл не выбран")

    def compress_with_huffman(self):
        output_file, _ = QFileDialog.getSaveFileName(self, "Сохранить сжатый файл", "", "Huffman Compressed (*.huff)")
        if not output_file:
            return

        try:
            start_time = time.time()  # Начало замера времени

            if hasattr(self, 'selected_file_for_huffman') and self.selected_file_for_huffman:
                # Сжатие файла
                original_size = os.path.getsize(self.selected_file_for_huffman)  # Размер исходного файла
                huffman_compress(self.selected_file_for_huffman, output_file)
                compressed_size = os.path.getsize(output_file)  # Размер сжатого файла
                self.ui.status.setText(f"Файл сжат: {os.path.basename(output_file)}")
            else:
                text = self.ui.origHuffmanText.toPlainText()
                if not text:
                    self.show_error_message("Ошибка", "Введите текст или выберите файл для сжатия!",
                                            QMessageBox.Warning)
                    return

                temp_input_file = "temp_huffman_input.txt"
                with open(temp_input_file, 'w', encoding='utf-8') as f:
                    f.write(text)

                original_size = os.path.getsize(temp_input_file)  # Размер исходного текста
                huffman_compress(temp_input_file, output_file)
                compressed_size = os.path.getsize(output_file)  # Размер сжатого файла
                os.remove(temp_input_file)
                self.ui.status.setText(f"Текст сжат: {os.path.basename(output_file)}")

            # Вычисление статистики
            end_time = time.time()
            compression_time = (end_time - start_time) * 1000  # Время в миллисекундах
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

            # Обновление интерфейса
            self.ui.compTimeHuf.setPlainText(f"{compression_time:.2f} мс")
            self.ui.OrigSizeHuf.setPlainText(f"{original_size} байт")
            self.ui.CompSizeHuf.setPlainText(f"{compressed_size} байт")
            self.ui.CompPercHuf.setPlainText(f"{compression_ratio:.2f}%")

        except Exception as e:
            self.show_error_message("Ошибка", f"Ошибка при сжатии: {str(e)}", QMessageBox.Critical)

    def select_file_for_huffman_decompress(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите файл для разжатия", "", "Huffman Compressed (*.huff)")
        if file:
            self.ui.uploaded_files_4.setText(os.path.basename(file))
            self.selected_file_for_huffman_decompress = file
            self.ui.status_4.setText("Файл выбран")
        else:
            self.ui.status_4.setText("Файл не выбран")

    def decompress_with_huffman(self):
        if not hasattr(self, 'selected_file_for_huffman_decompress'):
            self.show_error_message("Ошибка", "Сначала выберите файл!", QMessageBox.Warning)
            return

        output_file, _ = QFileDialog.getSaveFileName(self, "Сохранить разжатый файл", "", "Текстовые файлы (*.txt)")
        if output_file:
            try:
                huffman_decompress(self.selected_file_for_huffman_decompress, output_file)
                self.ui.status_4.setText(f"Успешная декомпрессия: {os.path.basename(output_file)}")
            except Exception as e:
                self.show_error_message("Ошибка", f"Ошибка при разжатии: {str(e)}", QMessageBox.Critical)

    # ========== LZ77 функционал ==========
    def compress_with_lz77(self):
        text = self.ui.OriginalText.toPlainText()
        if not text:
            self.show_error_message("Ошибка", "Введите текст для сжатия!", QMessageBox.Warning)
            return

        window_size = self.ui.WindowSize.value()
        buffer_size = self.ui.BufferSize.value()

        try:
            result = lz77_compress(text, window_size, buffer_size)

            self.ui.compressedResult.setPlainText(result['encoded_sequence'])

            self.ui.CompressionTime.setPlainText(f"{result['compression_time']:.2f} мс")
            self.ui.originalTextSize.setPlainText(f"{result['original_size']} байт")
            self.ui.compressedTextSize.setPlainText(f"{result['compressed_size']} байт")
            self.ui.CompressionPercentage.setPlainText(f"{result['compression_ratio']:.2f}%")

        except Exception as e:
            self.show_error_message("Ошибка", f"Ошибка при сжатии LZ77: {str(e)}", QMessageBox.Critical)

    def decompress_with_lz77(self):
        encoded_sequence = self.ui.compressedText.toPlainText().strip()
        if not encoded_sequence:
            self.show_error_message("Ошибка", "Введите закодированную последовательность!", QMessageBox.Warning)
            return

        window_size = self.ui.WindowSize.value()
        buffer_size = self.ui.BufferSize.value()

        try:
            result = lz77_decompress_from_sequence(encoded_sequence, window_size, buffer_size)

            self.ui.decompressedText.setPlainText(result['decompressed_text'])

            self.ui.decompressionTimeStat.setPlainText(f"{result['decompression_time']:.2f} мс")
            self.ui.CompressedSizeStat.setPlainText(f"{result['compressed_size']} байт")
            self.ui.DecompressedSizeStat.setPlainText(f"{result['decompressed_size']} байт")

        except Exception as e:
            self.show_error_message("Ошибка", f"Ошибка при декомпрессии LZ77: {str(e)}", QMessageBox.Critical)

    # ========== Deflate функционал ==========
    def select_file_for_deflate(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите файл для сжатия", "", "Текстовые файлы (*.txt)")
        if file:
            self.ui.chosenFile_3.setText(os.path.basename(file))
            self.selected_file_for_deflate = file
            self.ui.OriginalText_3.clear()
        else:
            self.ui.chosenFile_3.setText("Выбранный файл: ")

    def compress_with_deflate(self):
        output_file, _ = QFileDialog.getSaveFileName(self, "Сохранить сжатый файл", "",
                                                     "Deflate Compressed (*.deflate)")
        if not output_file:
            return

        try:
            if hasattr(self, 'selected_file_for_deflate') and self.selected_file_for_deflate:
                with open(self.selected_file_for_deflate, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                text = self.ui.OriginalText_3.toPlainText()
                if not text:
                    self.show_error_message("Ошибка", "Введите текст или выберите файл для сжатия!",
                                            QMessageBox.Warning)
                    return

            result = deflate_compress(text)

            with open(output_file, 'wb') as f:
                f.write(result['compressed_bytes'])

            self.ui.compTime.setPlainText(f"{result['compression_time']:.2f} мс")
            self.ui.OrigSize.setPlainText(f"{result['original_size']} байт")
            self.ui.CompSize.setPlainText(f"{result['compressed_size']} байт")
            self.ui.CompPerc.setPlainText(f"{result['compression_ratio']:.2f}%")

        except Exception as e:
            self.show_error_message("Ошибка", f"Ошибка при сжатии Deflate: {str(e)}", QMessageBox.Critical)

    def select_file_for_deflate_decompress(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите файл для разжатия", "", "Deflate Compressed (*.deflate)")
        if file:
            self.ui.uploaded_files_5.setText(os.path.basename(file))
            self.selected_file_for_deflate_decompress = file
            self.ui.status_5.setText("Файл выбран")
        else:
            self.ui.status_5.setText("Файл не выбран")

    def decompress_with_deflate(self):
        if not hasattr(self, 'selected_file_for_deflate_decompress') or not self.selected_file_for_deflate_decompress:
            self.show_error_message("Ошибка", "Сначала выберите файл!", QMessageBox.Warning)
            return

        output_file, _ = QFileDialog.getSaveFileName(self, "Сохранить разжатый файл", "", "Текстовые файлы (*.txt)")
        if output_file:
            try:
                with open(self.selected_file_for_deflate_decompress, 'rb') as f:
                    compressed_bytes = f.read()
                result = deflate_decompress(compressed_bytes)

                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result['decompressed_text'])

                self.ui.status_5.setText(f"Успешная декомпрессия: {os.path.basename(output_file)}")
            except Exception as e:
                self.show_error_message("Ошибка", f"Ошибка при разжатии Deflate: {str(e)}", QMessageBox.Critical)

    # ========== Brotli функционал ==========
    def select_file_for_brotli(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите файл для сжатия", "", "Текстовые файлы (*.txt)")
        if file:
            self.ui.ChosenFileBrotli.setText(os.path.basename(file))
            self.selected_file_for_brotli = file
            self.ui.status_2.setText("Файл выбран")
            self.ui.origTextBrotli.clear()
        else:
            self.ui.status_2.setText("Файл не выбран")

    def compress_with_brotli(self):
        output_file, _ = QFileDialog.getSaveFileName(self, "Сохранить сжатый файл", "", "Brotli Compressed (*.br)")
        if not output_file:
            return

        try:
            if hasattr(self, 'selected_file_for_brotli') and self.selected_file_for_brotli:
                # Compress file
                result = brotli_compress(self.selected_file_for_brotli)
                self.ui.status_2.setText(f"Файл сжат: {os.path.basename(output_file)}")
            else:
                text = self.ui.origTextBrotli.toPlainText()
                if not text:
                    self.show_error_message("Ошибка", "Введите текст или выберите файл для сжатия!",
                                            QMessageBox.Warning)
                    return
                # Compress text
                result = brotli_compress(text)

            # Save compressed data
            with open(output_file, 'wb') as f:
                f.write(result['compressed_bytes'])

            # Update UI with statistics
            self.ui.compTimeBrotli.setPlainText(f"{result['compression_time']:.2f} мс")
            self.ui.OrigSizeBrotli.setPlainText(f"{result['original_size']} байт")
            self.ui.CompSizeBrotli.setPlainText(f"{result['compressed_size']} байт")
            self.ui.CompPercBrotli.setPlainText(f"{result['compression_ratio']:.2f}%")

        except Exception as e:
            self.show_error_message("Ошибка", f"Ошибка при сжатии Brotli: {str(e)}", QMessageBox.Critical)

    def select_file_for_brotli_decompress(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите файл для разжатия", "", "Brotli Compressed (*.br)")
        if file:
            self.ui.uploadedFilesBrotli.setText(os.path.basename(file))
            self.selected_file_for_brotli_decompress = file
            self.ui.statusBrotli.setText("Файл выбран")
        else:
            self.ui.statusBrotli.setText("Файл не выбран")

    def decompress_with_brotli(self):
        if not hasattr(self, 'selected_file_for_brotli_decompress') or not self.selected_file_for_brotli_decompress:
            self.show_error_message("Ошибка", "Сначала выберите файл!", QMessageBox.Warning)
            return

        output_file, _ = QFileDialog.getSaveFileName(self, "Сохранить разжатый файл", "", "Текстовые файлы (*.txt)")
        if output_file:
            try:
                result = brotli_decompress(self.selected_file_for_brotli_decompress)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result['decompressed_text'])
                self.ui.statusBrotli.setText(f"Успешная декомпрессия: {os.path.basename(output_file)}")
            except Exception as e:
                self.show_error_message("Ошибка", f"Ошибка при разжатии Brotli: {str(e)}", QMessageBox.Critical)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
