import streamlit as st
import pandas as pd
from fpdf import FPDF


def product_lookup(df, product_code):
    """Looks up a product by code and returns its details."""
    product = df[df['Product Code'] == int(product_code)]
    if not product.empty:
        return product.iloc[0]['Description'], product.iloc[0]['Price']
    return None, None

def generate_pdf(customer_data, billing_items, net_total):
    """Generates a PDF invoice."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Header

    pdf.cell(200, 10, txt="OSAKA AUTO PARTS LLC", ln=True, align="C")
    pdf.cell(200, 10, txt="29 AL Musalla Road, Deira, Dubai ", ln=True, align="C")
    pdf.cell(200, 10, txt="Invoice", ln=True, align="C")
    pdf.cell(200, 10, txt="________________________________________________________________", ln=True, align="C")
    pdf.ln(10)  # space

    # Customer Information
    pdf.cell(200, 10, txt="Customer Information", ln=True, align="L")
    pdf.cell(60, 10, txt=f"Name: {customer_data['name']}", ln=True, align="L")
    pdf.cell(60, 10, txt=f"Address: {customer_data['address']}", ln=True, align="L")
    pdf.cell(60, 10, txt=f"Email: {customer_data['email']}", ln=True, align="L")
    pdf.cell(60, 10, txt=f"Phone: {customer_data['phone']}", ln=True, align="L")
    pdf.ln(10)

    # Billing Items Table
    pdf.cell(20, 10, txt="Code", border=1)
    pdf.cell(80, 10, txt="Description", border=1)
    pdf.cell(30, 10, txt="Qty", border=1)
    pdf.cell(30, 10, txt="Price", border=1)
    pdf.cell(30, 10, txt="Total", border=1, ln=True)

    for item in billing_items:
        pdf.cell(20, 10, txt=str(item['code']), border=1)
        pdf.cell(80, 10, txt=item['description'], border=1)
        pdf.cell(30, 10, txt=str(item['quantity']), border=1)
        pdf.cell(30, 10, txt=str(item['price']), border=1)
        pdf.cell(30, 10, txt=str(item['total']), border=1, ln=True)

    pdf.ln(5)
    pdf.cell(170, 10, txt="Net Total:", border=0, align="R")
    pdf.cell(30, 10, txt=str(net_total), border=1, ln=True)

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return pdf_bytes


# --- Streamlit App ---
st.title("OSAKA AUTO PARTS LLC Billing App")
st.write("Upload your product Excel file and generate invoices.")

# File Upload
uploaded_file = st.file_uploader("Upload Product Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.subheader("Uploaded Data Preview")
        st.dataframe(df)

        # Initialize Billing Items list in Session State
        if 'billing_items' not in st.session_state:
            st.session_state['billing_items'] = []

        # Billing Section
        st.subheader("Add Product")
        col1, col2, col3 = st.columns(3)
        with col1:
            product_code = st.text_input("Product Code")
        with col2:
            quantity = st.number_input("Quantity", min_value=1, step=1)
        add_product_btn = col3.button("Add Product")

        if add_product_btn:
            if product_code and quantity:
                description, price = product_lookup(df, product_code)
                if description and price:
                    total = price * quantity
                    st.session_state['billing_items'].append({
                        "code": product_code,
                        "description": description,
                        "quantity": quantity,
                        "price": price,
                        "total": total
                    })
                    st.success(f"Product {product_code} added to the bill.")
                else:
                    st.error("Invalid Product Code.")
            else:
                st.error("Please enter product code and quantity")

        # Display Current Bill Items
        st.subheader("Current Billing Items")
        if st.session_state['billing_items']:
            bill_df = pd.DataFrame(st.session_state['billing_items'])
            st.dataframe(bill_df)

            # Remove Item functionality
            selected_index = st.selectbox('Select Item to Remove',
                                        options=range(len(st.session_state['billing_items'])),
                                        format_func=lambda x: f"Index: {x} Code: {st.session_state['billing_items'][x]['code']}")
            remove_item_btn = st.button('Remove Item')
            if remove_item_btn:
                st.session_state['billing_items'].pop(selected_index)
                st.session_state  # refresh the page after removing an item


            # Calculate Net Total
            net_total = sum(item['total'] for item in st.session_state['billing_items'])
            st.write(f"Net Total: {net_total}")

        else:
            st.write("No items in the bill yet.")

        # Customer Information
        st.subheader("Customer Details")
        customer_data = {}
        customer_data['name'] = st.text_input("Name")
        customer_data['address'] = st.text_input("Address")
        customer_data['email'] = st.text_input("Email")
        customer_data['phone'] = st.text_input("Phone Number")

        # PDF Generation
        if st.button("Generate Invoice"):
            if st.session_state['billing_items'] and customer_data['name'] and customer_data['address'] and customer_data['email'] and customer_data['phone']:
                pdf_file = generate_pdf(customer_data, st.session_state['billing_items'], net_total)
                st.download_button(
                    label="Download Invoice PDF",
                    data=pdf_file,
                    file_name="invoice.pdf",
                    mime="application/pdf",
                )
                st.success("PDF Invoice generated Successfully")

            else:
                st.error("Please fill in all the details and Add Product to the invoice.")
    except Exception as e:
        st.error(f"Error processing the file: {e}")