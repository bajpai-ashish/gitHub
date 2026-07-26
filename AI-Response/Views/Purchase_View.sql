-- my_warehouse.main.Purchases_Invoice source

CREATE OR REPLACE VIEW Purchases_Invoice AS
SELECT
    purchase.WWI_Purchase_Order_ID AS "Purchase Number",
    purchase_date.Date AS "Purchased  or Order Dates",
    purchase_date.Day_Number AS "Purchased  or Order Day Number",
    purchase_date."Day" AS "Purchased  or Order Day",
    purchase_date."Month" AS "Purchased  or Order Month Name",
    purchase_date.Short_Month AS "Purchased  or Order Short Month Name",
    purchase_date.Calendar_Month_Number AS "Purchased  or Order Month Number",
    purchase_date.Calendar_Month_Label AS "Purchased  or Order Calendar Month Name",
    purchase_date.Calendar_Year AS "Purchased  or Order Year Number",
    purchase_date.Calendar_Year_Label AS "Purchased  or Order Calendar Year Name",
    purchase_date.Fiscal_Month_Number AS "Purchased  or Order Financial Month Number",
    purchase_date.Fiscal_Month_Label AS "Purchased  or Order Financial Month Name",
    purchase_date.Fiscal_Year AS "Purchased  or Order Financial Year",
    purchase_date.Fiscal_Year_Label AS "Purchased  or Order Financial Year Name",
    purchase_date.ISO_Week_Number AS "Purchased  or Order Week Number",
    supplier.WWI_Supplier_ID AS "Supplier Code",
    supplier.Supplier AS "Supplier Name",
    supplier.Category AS "Supplier Category",
    supplier.Primary_Contact AS "Primary Contact",
    supplier.Supplier_Reference AS "Supplier Reference",
    supplier.Payment_Days AS "Payment Days",
    supplier.Postal_Code AS "Postal Code",
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
    purchase.Ordered_Outers AS "Ordered Outers",
    purchase.Ordered_Quantity AS "Ordered Quantity",
    purchase.Received_Outers AS "Received Outers",
    purchase.Package AS "Purchases Package",
    purchase.Is_Order_Finalized AS "Is Purchases Finalized"
FROM
    iceberg_scan('file:///C:/data/data_files/iceberg/WideWorldImportersDW/fact/purchase', ("version" = '?'), (allow_moved_paths = CAST('t' AS BOOLEAN))) AS purchase
LEFT JOIN iceberg_scan('file:///C:/data/data_files/iceberg/WideWorldImportersDW/dimension/date', ("version" = '?'), (allow_moved_paths = CAST('t' AS BOOLEAN))) AS purchase_date ON
    ((purchase.Date_Key = purchase_date.Date))
LEFT JOIN iceberg_scan('file:///C:/data/data_files/iceberg/WideWorldImportersDW/dimension/supplier', ("version" = '?'), (allow_moved_paths = CAST('t' AS BOOLEAN))) AS supplier ON
    ((purchase.Supplier_Key = supplier.Supplier_Key))
LEFT JOIN iceberg_scan('file:///C:/data/data_files/iceberg/WideWorldImportersDW/dimension/Stock_Item', ("version" = '?'), (allow_moved_paths = CAST('t' AS BOOLEAN))) AS Stock_Item ON
    ((purchase.Stock_Item_Key = Stock_Item.Stock_Item_Key));