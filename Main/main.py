import os
import sys
from PySide6.QtWidgets import QApplication

# ensure project root is on sys.path so package imports like Controller and View work
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
	sys.path.insert(0, ROOT)
from DataBase.db_connection import Connection
from View.main_widget import MainWindow
from View.theme import ThemeBuilder

from Controller.clock_controller import ClockController
from Controller.main_controller import MainController
from Controller.project_controller import ProjectController
from View.pet_widget import PetWidget
from View.settings_widget import SettingsWidget
from View.project_widget import ProjectsWidget
from View.whiteNoise_widget import WhiteNoiseWidget

def main() -> None:
	app = QApplication(sys.argv)
	
	# apply global theme
	builder = ThemeBuilder()
	app.setStyleSheet(builder.stylesheet())
	db_connection = Connection("pomo_pet.db")
	project_controller = ProjectController(db_connection)
	clock_controller = ClockController()
	c = clock_controller.view
	Pet = PetWidget()
	Pet.complete_day(1)
	Pet.complete_day(2)
	S = SettingsWidget()
	T = ProjectsWidget()
	project_controller.set_view(T)
	main_controller = MainController(clock_controller, project_controller)
	w = WhiteNoiseWidget()
	main_view = MainWindow(c,Pet,T,w,S)
	main_view.show()

	sys.exit(app.exec())


if __name__ == "__main__":
	main()

