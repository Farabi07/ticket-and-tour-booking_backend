# utils.py
def generate_seat_name(row, col, seat_plan):
    if seat_plan == 'number':
        seat_number = row * 4 + col + 1
        if seat_number < 10:
            return f"0{seat_number}"
        else:
            return str(seat_number)
    else:
        row_name = chr(65 + row)  # 'A' for row 0, 'B' for row 1, and so on
        return f"{row_name}{col + 1}"
# def generate_seat_name(row, col, seat_plan):
#     if seat_plan == 'number':
#         return f"{col + 1:02d}"  # Use f-strings to format with leading zeros
#     else:
#         row_name = chr(65 + row)  # 'A' for row 0, 'B' for row 1, and so on
#         return f"{row_name}{col + 1:02d}"