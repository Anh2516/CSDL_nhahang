import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# ---------- KẾT NỐI CSDL ----------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="new_password",  
    database="QuanLyNhaHang"
)
cursor = conn.cursor()

# ---------- HÀM DÙNG CHUNG ----------
def xoa_bang(tree):
    for item in tree.get_children():
        tree.delete(item)
def nap_du_lieu(tree, table, columns):
    xoa_bang(tree)
    try:
        cursor.execute(f"SELECT {', '.join(columns)} FROM {table}")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
    except mysql.connector.Error as err:
        messagebox.showerror("Lỗi", str(err))

# ---------- GIAO DIỆN QUẢN LÝ ----------
def tao_quan_ly(tab, table, columns, headers):
    tree = ttk.Treeview(tab, columns=columns, show='headings')
    for i, col in enumerate(columns):
        tree.heading(col, text=headers[i])
        tree.column(col, width=150)
    tree.pack(fill='both', expand=True, pady=5)

    # Tạo entry nhập dữ liệu
    entries = {}
    entry_frame = tk.Frame(tab)
    entry_frame.pack(pady=5)

    for i, col in enumerate(columns):
        tk.Label(entry_frame, text=headers[i]).grid(row=0, column=i)
        ent = tk.Entry(entry_frame, width=15)
        ent.grid(row=1, column=i, padx=3)
        entries[col] = ent

    # Xóa ô nhập
    def clear_entries():
        for ent in entries.values():
            ent.delete(0, tk.END)

    # Chọn dòng → hiện vào entry
    def chon_dong(event):
        selected = tree.selection()
        if selected:
            values = tree.item(selected[0])["values"]
            for i, col in enumerate(columns):
                entries[col].delete(0, tk.END)
                entries[col].insert(0, values[i])

    tree.bind("<<TreeviewSelect>>", chon_dong)

    # Thêm dữ liệu
    def them():
        values = [entries[col].get() for col in columns]
        if any(v == "" for v in values):
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ.")
            return
        try:
            sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['%s']*len(columns))})"
            cursor.execute(sql, values)
            conn.commit()
            nap_du_lieu(tree, table, columns)
            clear_entries()
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Lỗi thêm: {err}")

    # Sửa dữ liệu
    def sua():
        values = [entries[col].get() for col in columns]
        if any(v == "" for v in values):
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ.")
            return
        try:
            set_clause = ', '.join([f"{col}=%s" for col in columns[1:]])
            sql = f"UPDATE {table} SET {set_clause} WHERE {columns[0]}=%s"
            cursor.execute(sql, values[1:] + [values[0]])
            conn.commit()
            nap_du_lieu(tree, table, columns)
            clear_entries()
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Lỗi sửa: {err}")

    # Xóa dữ liệu
    def xoa():
        ma = entries[columns[0]].get()
        if not ma:
            messagebox.showwarning("Chọn dòng", "Vui lòng chọn dòng để xóa.")
            return
        try:
            cursor.execute(f"DELETE FROM {table} WHERE {columns[0]}=%s", (ma,))
            conn.commit()
            nap_du_lieu(tree, table, columns)
            clear_entries()
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Lỗi xóa: {err}")

    # Các nút chức năng
    btn_frame = tk.Frame(tab)
    btn_frame.pack(pady=5)
    ttk.Button(btn_frame, text="Thêm", command=them).pack(side='left', padx=5)
    ttk.Button(btn_frame, text="Sửa", command=sua).pack(side='left', padx=5)
    ttk.Button(btn_frame, text="Xóa", command=xoa).pack(side='left', padx=5)


    nap_du_lieu(tree, table, columns)

# ---------- GIAO DIỆN CHÍNH ----------
root = tk.Tk()
root.title("Quản lý Nhà hàng")
root.geometry("1000x600")

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Quản lý Nhân viên
tab_nv = ttk.Frame(notebook)
notebook.add(tab_nv, text="Nhân viên")
tao_quan_ly(tab_nv, "NhanVien", ["ma_nv", "ho_ten", "sdt"], ["Mã NV", "Họ tên", "SĐT"])

# Quản lý Món ăn
tab_ma = ttk.Frame(notebook)
notebook.add(tab_ma, text="Món ăn")
tao_quan_ly(tab_ma, "MonAn", ["ma_mon_an", "ten_mon_an", "gia","ma_nguyen_lieu_mon_an"], ["Mã món", "Tên món", "Giá", "Mã nguyên liệu món ăn"])

# Quản lý đặt bàn
tab_db = ttk.Frame(notebook)
notebook.add(tab_db, text="Đặt bàn")
tao_quan_ly(tab_db, "DatBan", ["ma_dat_ban", "ma_khach_hang", "ma_ban", "trang_thai"], ["Mã Đặt bàn", "Mã KH", "Mã Bàn", "Trạng thái"])

# Quản ly hoa đơn
tab_hd = ttk.Frame(notebook)
notebook.add(tab_hd, text="Hóa đơn")
tao_quan_ly(tab_hd, "HoaDon", ["ma_hoa_don", "so_tien", "don_vi_tien_te", "ma_kh"], ["Mã Hóa đơn", "Số tiền", "Đơn vị tiền tệ", "Mã KH"])

# Quản lý chi tiết đặt bàn
tab_ctdb = ttk.Frame(notebook)
notebook.add(tab_ctdb, text="Chi tiết đặt bàn")
tao_quan_ly(tab_ctdb, "ChiTietDatBan", ["ma_chi_tiet_dat_ban", "ma_dat_ban", "ngay_gio_dat", "ngay_hen","so_luong_nguoi"], ["Mã CT Đặt bàn", "Mã Đặt bàn", "Ngày giờ đặt", "Ngày hẹn", "Số lượng người"])

# Quản lý Khách hàng
tab_kh = ttk.Frame(notebook)
notebook.add(tab_kh, text="Khách hàng")
tao_quan_ly(tab_kh, "KhachHang", ["ma_khach_hang", "ho_ten", "sdt"], ["Mã KH", "Họ tên", "SĐT"])

root.mainloop()
