import sys
import unittest
from view import MainWindow

if __name__ == "__main__":
    if "--test" in sys.argv:
        # Удаляем все аргументы, оставляя только имя скрипта
        sys.argv = [sys.argv[0]]
        import test_model
        unittest.main()
    else:
        app = MainWindow()
        app.mainloop()