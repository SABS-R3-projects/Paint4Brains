import os
import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QRect
from Paint4Brains.GUI.MainWindow import MainWindow
from Paint4Brains.GUI.MainWidget import MainWidget


class TestMainWindow(unittest.TestCase):
    """Test a few GUI methods.

    Due to the limitations of testing PyQt5 applications with QTest the tests here a quite limited.
    """
    root_dir = os.path.dirname(os.path.dirname(__file__))
    filename = os.path.join(root_dir, '../Paint4Brains/opensource_brains/H_F_22.nii')
    app = QApplication(['-platform', 'minimal'])
    main = MainWindow(filename)

    def test_MainWindow_title(self):
        """Simple test to test that testing is feasible.
        """
        # For MainWindow check the title:
        self.assertEqual(self.main.windowTitle(), "Paint4Brains")

    def test_MainWindow_starts(self):
        """Testing that the GUI starts as expected.
        """
        # Try and open MainWindow:
        self.main.show()
        QTest.qWaitForWindowExposed(self.main)

    def test_MainWindow_shortcuts(self):
        """Testing some of the simpler shortcuts do what you would expect them to
        """
        # First open MainWindow:
        self.main.show()
        QTest.qWaitForWindowExposed(self.main)

        # Test Enable/Disable drawing
        old = self.main.main_widget.win.view.drawing
        QTest.keyClick(self.main, "d", Qt.ControlModifier)
        assert self.main.main_widget.win.view.drawing != old

        # Test View All labels
        old = self.main.main_widget.win.see_all_labels
        QTest.keyClick(self.main, "a", Qt.ControlModifier)
        assert self.main.main_widget.win.see_all_labels != old

        # Test adjust slice intensity
        old = self.main.hist_widget.isVisible()
        QTest.keyClick(self.main, "h", Qt.ControlModifier)
        QTest.qWaitForWindowExposed(self.main.hist_widget)
        assert self.main.hist_widget.isVisible() != old

    def test_view_recentering(self):
        """Testing the image recenter function
        """
        main_widget = MainWidget(self.main.brain)

        # Where is the brain usually?
        usual = main_widget.win.view.viewRect()

        # Reshape and move
        main_widget.win.view.setRange(QRect(0, 0, 2 * usual.height(), 2 * usual.width()))

        # Size should be different
        assert usual != main_widget.win.view.viewRect()

        # Recenter
        main_widget.win.recenter()

        # Size should be the same now
        assert usual == main_widget.win.view.viewRect()
