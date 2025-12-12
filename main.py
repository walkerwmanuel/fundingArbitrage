# main.py
from logic.ml import get_expected_return

if __name__ == "__main__":
    ex_return = get_expected_return('SOL')
    print(ex_return)