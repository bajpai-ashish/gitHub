-- my_warehouse.main.Sale_Invoice source

CREATE OR REPLACE VIEW Sale_Invoice
AS
    SELECT
        fs.WWI_Invoice_ID AS "Invoice ID",
        ct.WWI_City_ID AS "City Code",
        ct.City AS "City Name",
        ct.State_Province AS "State or Province",
        ct.Country AS Country,
        ct.Continent AS Continent,
        ct.Sales_Territory AS "Sales Territory",
        ct.Region AS Region,
        ct.Subregion AS Subregion,
        ct.Latest_Recorded_Population AS "Latest Recorded Population in City",
        c.WWI_Customer_ID AS "Customer Code",
        c.Customer AS "Customer Full Name",
        c.Bill_To_Customer AS "Billing Customer Full Name",
        c.Category AS "Customer Category",
        c.Buying_Group AS "Customer Buying Group",
        c.Primary_Contact AS "Customer Primary Contact",
        c.Postal_Code AS "Customer Postal Code",
        cbill.WWI_Customer_ID AS "Billing Customer Code",
        cbill.Customer AS "Billing Customer Full Name",
        cbill.Bill_To_Customer AS "Billing Customer Full Name",
        cbill.Category AS "Billing Customer Category",
        cbill.Buying_Group AS "Billing Customer Buying Group",
        cbill.Primary_Contact AS "Billing Customer Primary Contact",
        cbill.Postal_Code AS "Billing Customer Postal Code",
        Stock_Item.WWI_Stock_Item_ID AS "Item ID",
        Stock_Item.Stock_Item AS "Item Name",
        Stock_Item.Color AS "Item Color",
        Stock_Item.Selling_Package AS "Item Selling Package",
        Stock_Item.Buying_Package AS "Item Buying Package",
        Stock_Item.Brand AS "Item Brand",
        Stock_Item.Size AS "Item Size",
        Stock_Item.Lead_Time_Days AS "ItemLead Time Days",
        Stock_Item.Quantity_Per_Outer AS "Item Quantity Per Outer",
        Stock_Item.Is_Chiller_Stock AS "Is Chiller Item",
        Stock_Item.Barcode AS "Item Barcode",
        Stock_Item.Tax_Rate AS "Item Tax Rate",
        Stock_Item.Unit_Price AS "Item Unit Price",
        Stock_Item.Recommended_Retail_Price AS "Item Recommended Retail Price",
        Stock_Item.Typical_Weight_Per_Unit AS "Item Typical Weight Per Unit",
        inv_date.Date AS "Invoice Dates",
        inv_date.Day_Number AS "Invoice Day Number",
        inv_date."Day" AS "Invoice Day",
        inv_date."Month" AS "Invoice Month Name",
        inv_date.Short_Month AS "Invoice Short Month Name",
        inv_date.Calendar_Month_Number AS "Invoice Month Number",
        inv_date.Calendar_Month_Label AS "Invoice Calendar Month Name",
        inv_date.Calendar_Year AS "Invoice Year Number",
        inv_date.Calendar_Year_Label AS "Invoice Calendar Year Name",
        inv_date.Fiscal_Month_Number AS "Invoice Financial Month Number",
        inv_date.Fiscal_Month_Label AS "Invoice Financial Month Name",
        inv_date.Fiscal_Year AS "Invoice Financial Year",
        inv_date.Fiscal_Year_Label AS "Invoice Financial Year Name",
        inv_date.ISO_Week_Number AS "Invoice Week Number",
        del_date.Date AS "Delivery Dates",
        del_date.Day_Number AS "Delivery Day Number",
        del_date."Day" AS "Delivery Day",
        del_date."Month" AS "Delivery Month Name",
        del_date.Short_Month AS "Delivery Short Month Name",
        del_date.Calendar_Month_Number AS "Delivery Month Number",
        del_date.Calendar_Month_Label AS "Delivery Calendar Month Name",
        del_date.Calendar_Year AS "Delivery Year Number",
        del_date.Calendar_Year_Label AS "Delivery Calendar Year Name",
        del_date.Fiscal_Month_Number AS "Delivery Financial Month Number",
        del_date.Fiscal_Month_Label AS "Delivery Financial Month Name",
        del_date.Fiscal_Year AS "Delivery Financial Year",
        del_date.Fiscal_Year_Label AS "Delivery Financial Year Name",
        del_date.ISO_Week_Number AS "Delivery Week Number",
        employee.Employee AS "Employee Full Name",
        employee.Preferred_Name AS "Employee Calling Name",
        fs.Description AS "Billing Note Description / Annotation",
        fs.Package AS "Packaging Type",
        fs.Quantity AS "Sale Quantity",
        fs.Unit_Price AS "Unit Price of Item",
        fs.Tax_Rate AS "Tax Rate on Item",
        fs.Total_Excluding_Tax AS "Total Excluding Tax on Invoice",
        fs.Tax_Amount AS "Tax Amount on Item",
        fs.Profit AS "Earned Profit on Invoice",
        fs.Total_Including_Tax AS "Tax Amount on Invoice",
        fs.Total_Dry_Items AS "Total Item can be stored in Dry Place",
        fs.Total_Chiller_Items AS "Total Item need stored in cooler or child Place"
    FROM
        iceberg_scan('file:///C:/data/data_files/iceberg/WideWorldImportersDW/fact/sale', ("version" = '?'), (allow_moved_paths = CAST
('t' AS BOOLEAN))) AS fs
LEFT JOIN iceberg_scan
('file:///C:/data/data_files/iceberg/WideWorldImportersDW/dimension/customer',
("version" = '?'),
(allow_moved_paths = CAST
('t' AS BOOLEAN))) AS c ON
((fs.Customer_Key = c.Customer_Key))
LEFT JOIN iceberg_scan
('file:///C:/data/data_files/iceberg/WideWorldImportersDW/dimension/customer',
("version" = '?'),
(allow_moved_paths = CAST
('t' AS BOOLEAN))) AS cbill ON
((fs.Bill_To_Customer_Key = cbill.Customer_Key))
LEFT JOIN iceberg_scan
('file:///C:/data/data_files/iceberg/WideWorldImportersDW/dimension/city',
("version" = '?'),
(allow_moved_paths = CAST
('t' AS BOOLEAN))) AS ct ON
((fs.city_key = ct.city_key))
LEFT JOIN iceberg_scan
('file:///C:/data/data_files/iceberg/WideWorldImportersDW/dimension/Stock_Item',
("version" = '?'),
(allow_moved_paths = CAST
('t' AS BOOLEAN))) AS Stock_Item ON
((fs.Stock_Item_Key = Stock_Item.Stock_Item_Key))
LEFT JOIN iceberg_scan
('file:///C:/data/data_files/iceberg/WideWorldImportersDW/dimension/employee',
("version" = '?'),
(allow_moved_paths = CAST
('t' AS BOOLEAN))) AS employee ON
((fs.Salesperson_key = employee.Employee_Key))
LEFT JOIN iceberg_scan
('file:///C:/data/data_files/iceberg/WideWorldImportersDW/dimension/date',
("version" = '?'),
(allow_moved_paths = CAST
('t' AS BOOLEAN))) AS inv_date ON
((fs.Invoice_Date_Key = inv_date.Date))
LEFT JOIN iceberg_scan
('file:///C:/data/data_files/iceberg/WideWorldImportersDW/dimension/date',
("version" = '?'),
(allow_moved_paths = CAST
('t' AS BOOLEAN))) AS del_date ON
((fs.Delivery_Date_Key = del_date.Date));