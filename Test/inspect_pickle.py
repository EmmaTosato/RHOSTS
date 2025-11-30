import pickle
import sys
sys.path.append("/data/etosato/RHOSTS/High_order_TS_with_scaffold")

filepath = "/data/etosato/RHOSTS/Output/lorenzo_data/134829/generators/generators__100.pck"
try:
    with open(filepath, "rb") as f:
        data = pickle.load(f)
        print(f"Type: {type(data)}")
        print(f"Content: {data}")
        if hasattr(data, '__len__'):
            print(f"Length: {len(data)}")
except Exception as e:
    print(f"Error: {e}")
