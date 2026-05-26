from pipeline import run_search_pipeline
from rich import print
import tools

if __name__ == "__main__":
    topic = input("Enter the Research topics:")
    final_state = run_search_pipeline(topic)
    print("\n" + " =" * 50)
    print("Final State: \n", final_state)