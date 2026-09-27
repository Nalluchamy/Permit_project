# PermitMaster — End-User Operational Guide (v1.0.0)

**Target Audience:** Dispatch Clerks & Staff Users  
**System:** PermitMaster TN Mining Dispatch Permit System

---

## 1. Logging In

1. Launch **PermitMaster** from your Desktop shortcut or Start Menu.
2. Enter your assigned **Username** and **Password**.
3. Click **Login**.
4. Upon successful authentication, the main **Dispatch Dashboard** will open.

---

## 2. Creating a Mining Dispatch Permit

1. On the main Dashboard, navigate to the **New Permit** tab.
2. Fill out all required permit fields:
   - **Serial Number:** Unique permit serial (e.g. `TN03996631`)
   - **Minecode / Lessee Details:** Minecode, Lessee Name, Address, HSN Code, District, Taluk, Village, SF No, Classification, Lease Period, Mineral Name, Bulk Permit, Order Reference, Within TN status.
   - **Dispatch Information:** Dispatch Slip Number, Delivered To, Quantity (MT), Authorized Person.
   - **Vehicle & Route Details:** Vehicle Number (e.g. `TN 30 AA 1234`), Vehicle Type, Distance (Kms), Destination, Via.
   - **Traveling Details:** Traveling Date (`DD-MM-YYYY`), Traveling Time (`HH:MM AM/PM`), Required Time (hrs).
   - **Driver Details:** Driver Name, License Number, Phone Number.
3. Click **Save & Generate PDF**.
4. The system validates all fields (checking for correct date formats, non-negative numbers, max field lengths, and duplicate serial numbers).
5. Upon successful validation, the record is stored in the database and the PDF permit is generated.

---

## 3. Printing & PDF Export

1. After permit generation, click **Print Permit** or open the generated PDF from `%LOCALAPPDATA%\PermitMaster\generated_pdfs\`.
2. The generated PDF contains two identical permit blocks:
   - **Top Block:** Office Copy
   - **Bottom Block:** Driver Copy
3. When printing, select **A4 Paper Size** and set scaling to **100% (Actual Size / Do Not Scale)**.
4. Each copy includes a high-clarity **QR Code** for instant field verification.

---

## 4. Searching & Managing Permits

1. Click the **Search Permits** tab.
2. Enter a Vehicle Number, Serial Number, or Lessee Name into the search field.
3. Click **Search**.
4. Select a permit record from the results table to view details or generate a reprint PDF.
