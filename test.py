import pyautogui


def insert_value(arr, value, index):
    if index < 0 or index > len(arr):
        print(f"Invalid index {index}. Appending {value} to the end.")
        arr.append(value)
        return arr
    
    return arr[:index] + [value] + arr[index:]
    
a = [1, 2, 3, 4, 5, 6]
print(insert_value(a, 7, 2))