from Uchat.driver import run
import os

if __name__ == "__main__":

    # Set working directory, relatively, to root of project
    this_path = os.path.abspath(os.path.dirname(__file__))
    this_path += '/../'
    os.chdir(this_path)
    run()
