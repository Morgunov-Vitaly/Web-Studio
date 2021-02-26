from PyQt5.QtWidgets import QMessageBox


def pause_continue_notification_dialog(message, informative_text=None, detailed_text=None):
    dialog = QMessageBox()
    dialog.setWindowTitle('Выполните действие...')
    dialog.setGeometry(0, 100, 550, 225)
    dialog.setText(message)
    dialog.setIcon(QMessageBox.Information)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.setDefaultButton(QMessageBox.Ok)
    # dialog.buttonClicked.connect(self.pause_continue_action)

    if informative_text is not None:
        dialog.setInformativeText(informative_text)
    if detailed_text is not None:
        dialog.setDetailedText(detailed_text)

    dialog.exec_()
    return dialog.result()


def abort_continue_notification_dialog(message, informative_text=None, detailed_text=None):
    dialog = QMessageBox()
    dialog.setWindowTitle('Укажите дальнейшее действие...')
    dialog.setGeometry(0, 100, 550, 225)
    dialog.setText(message)
    dialog.setIcon(QMessageBox.Warning)
    dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Abort)
    dialog.setDefaultButton(QMessageBox.Ok)
    dialog.setEscapeButton(QMessageBox.Abort)
    # dialog.buttonClicked.connect(self.abort_continue_action)

    if informative_text is not None:
        dialog.setInformativeText(informative_text)
    if detailed_text is not None:
        dialog.setDetailedText(detailed_text)

    dialog.exec_()
    return dialog.result()
