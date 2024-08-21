import pdfkit
import boto3 as boto
import json
from datetime import datetime
import PyPDF2
from db import findInvoiceByReferenceNumber, findPaidDate
import os


def combine_pdfs(pdf_list, output_filename):
    # Create a PDF merger object
    pdf_merger = PyPDF2.PdfMerger()

    # Append each PDF file
    for pdf in pdf_list:
        print("pdf--->", pdf)
        pdf_merger.append(pdf)

    # Write the combined PDF to a file
    with open(output_filename, "wb") as output_pdf:
        pdf_merger.write(output_pdf)


def getDataFromS3(fileName):
    print("fileName: " + fileName)
    try:
        # initialize S3 bucket
        s3 = boto.client("s3")
        # get data from S3 bucket
        response = s3.get_object(
            Bucket="dev-sc-cdata-pipeline",
            Key=f"simplicapital/cdata/sci-surfaces/InvoiceLineItems/{fileName}",
        )
        #  read and decode data from S3 bucket
        file_content = response["Body"].read().decode("utf-8")
        # parse the data into JSON format
        data = json.loads(file_content)

        # return the data
        return data
    except Exception as error:
        print("Error---->", error)


def sciProcessData(event, flag=0, skip=0, invoiceName=None):
    try:
        print("hit------>")
        print("invoicename:--->", invoiceName)
        # get data from S3 bucket
        data = getDataFromS3(event["file_name"])
        # if invoiceName is None:
        #     invoiceName = []
        # # get data from database
        # invoices = findInvoiceByReferenceNumber(
        #     event["tenant"], event["invoice_ref_no"], skip
        # )
        # data = list(invoices)

        # store matched invoice
        matched_invoice = []
        # map the data
        for refNo in data:

            # find a particular invoice
            if event["invoice_ref_no"] == refNo["ReferenceNumber"]:
                if (
                    refNo["ItemIsGetPrintItemsInGroup"] is None
                    or refNo["ItemIsGetPrintItemsInGroup"] == None
                ):
                    print("hit------->filter")
                    # push the invoice into a array
                    matched_invoice.append(refNo)
        name = (
            f'{event["invoice_ref_no"]}_{flag}'
            if flag != 0
            else event["invoice_ref_no"]
        )

        print("matched_invoice---->", len(matched_invoice))

        # sent data to generateHtmlToPdf
        res = generateHtmlToPdf(matched_invoice, event, name)
        # if invoiceName != None:
        #     invoiceName.append(res)

        # if len(data) > 0:
        #     count = flag + 1
        #     print("hit recursive---->")
        #     skip_data = skip + 30
        #     sciProcessData(event, count, skip_data, invoiceName)

        return invoiceName
    except Exception as e:
        print("error---------->", e)


def generateHtmlToPdf(invoice_data, event, fileName):
    try:

        # formate date
        date = datetime.strptime(invoice_data[0]["Date"], "%Y-%m-%d")
        formatted_date_str = date.strftime("%-m/%-d/%Y")
        # format billing address
        BillingLine1 = (
            f"{invoice_data[0]['BillingLine1']} <br>"
            if invoice_data[0]["BillingLine1"] != ""
            else ""
        )
        BillingLine2 = (
            f"{invoice_data[0]['BillingLine2']} <br>"
            if invoice_data[0]["BillingLine2"] != ""
            else ""
        )
        BillingLine3 = (
            f"{invoice_data[0]['BillingLine3']} <br>"
            if invoice_data[0]["BillingLine3"] != ""
            else ""
        )
        BillingLine4 = (
            f"{invoice_data[0]['BillingLine4']} <br>"
            if invoice_data[0]["BillingLine4"] != ""
            else ""
        )
        BillingLine5 = (
            f"{invoice_data[0]['BillingLine5']} <br>"
            if invoice_data[0]["BillingLine5"] != ""
            else ""
        )
        BillingCity = (
            f"{invoice_data[0]['BillingCity']},"
            if invoice_data[0]["BillingCity"] != ""
            else ""
        )
        BillingState = (
            f"{invoice_data[0]['BillingState']},"
            if invoice_data[0]["BillingState"] != ""
            else ""
        )
        BillingPostalCode = (
            f"{invoice_data[0]['BillingPostalCode']}"
            if invoice_data[0]["BillingPostalCode"] != ""
            else ""
        )
        billing_address = f"""{BillingLine1} {BillingLine2} {BillingLine3} {BillingLine4} {BillingLine5} {BillingCity} {BillingState} {BillingPostalCode}"""
        paid = ""

        print("billing_address------->", billing_address)
        # is paid format
        # if invoice_data[0]["IsPaid"] == "true" or invoice_data[0]["IsPaid"] == True:

        #     paidDate = findPaidDate(event["tenant"], event["invoice_ref_no"])
        #     paidDate = paidDate["dtCollection"]
        #     paidDate = datetime.strptime(paidDate, "%Y-%m-%d")
        #     paidDate = paidDate.strftime("%m/%d/%Y")

        #     paid = f"""
        #   <div style= "position:absolute;z-index:1;top:89px;left:354px;">

        #     <img src= "https://allassets.s3.amazonaws.com/invoice-materials/paid.png" style="width:180px;position:relative"/>
        #     <span style= "font-size:24px;font-weight: bold;transform:rotate(-24deg);position:absolute;right:-6px;top:80px">{paidDate}<span>

        #   </div>
        #   """
        # format shipping address
        ShippingLine1 = (
            f"{invoice_data[0]['ShippingLine1']} <br>"
            if invoice_data[0]["ShippingLine1"] != ""
            else ""
        )
        ShippingLine2 = (
            f"{invoice_data[0]['ShippingLine2']} <br>"
            if invoice_data[0]["ShippingLine2"] != ""
            else ""
        )
        ShippingLine3 = (
            f"{invoice_data[0]['ShippingLine3']} <br>"
            if invoice_data[0]["ShippingLine3"] != ""
            else ""
        )
        ShippingLine4 = (
            f"{invoice_data[0]['ShippingLine4']} <br>"
            if invoice_data[0]["ShippingLine4"] != ""
            else ""
        )
        ShippingLine5 = (
            f"{invoice_data[0]['ShippingLine5']} <br>"
            if invoice_data[0]["ShippingLine5"] != ""
            else ""
        )

        ShippingCity = (
            invoice_data[0]["ShippingCity"] + ","
            if invoice_data[0]["ShippingCity"] != ""
            or invoice_data[0]["ShippingCity"] != None
            else ""
        )
        ShippingState = (
            invoice_data[0]["ShippingState"] + ","
            if invoice_data[0]["ShippingState"] != ""
            or invoice_data[0]["ShippingState"] != None
            else ""
        )
        ShippingPostalCode = (
            invoice_data[0]["ShippingPostalCode"]
            if invoice_data[0]["ShippingPostalCode"] != ""
            or invoice_data[0]["ShippingPostalCode"] != None
            else ""
        )

        shipping_address = f"""{ShippingLine1} {ShippingLine2} {ShippingLine3}{ShippingLine4} {ShippingLine5} {ShippingCity} {ShippingState} {ShippingPostalCode}"""
        print("shipping_address----->", shipping_address)
        # format P.O.No.
        poNo = invoice_data[0]["PONumber"] if invoice_data[0]["PONumber"] != "" else ""
        if len(poNo) > 17:
            poNo = f"{poNo[:18]}..."
        # format Terms
        terms = invoice_data[0]["Terms"] if invoice_data[0]["Terms"] != "" else ""
        # format SalesRep
        rep = invoice_data[0]["SalesRep"] if invoice_data[0]["SalesRep"] != "" else ""
        print("invoice--------------->", invoice_data[0])

        # format ItemDescription & amount

        formatAmount = ""
        ItemQuantity = ""
        desc = ""
        for index, item in enumerate(invoice_data):

            # # format item amount
            # amount = item["ItemAmount"] if item["ItemAmount"] != "" else ""
            # amount = amount if amount != None else ""
            # # format quantity
            # ItemQuantity = item["ItemQuantity"] if item["ItemQuantity"] != "" else ""
            # ItemQuantity = ItemQuantity if ItemQuantity != None else ""
            # # format description

            # formatAmount = f"{amount}.00" if isinstance(amount, int) else amount
            # if formatAmount != "":
            #     formatAmount = f"{float(formatAmount):.2f}"
            # format item description
            description = (
                item["ItemDescription"] if item["ItemDescription"] != "" else ""
            )
            description = description if description != None else ""
            print("description--->", description)
            if index > 2:
                desc += """
            <div class="page-break"></div>
            """
            desc += f"""
                  <td style="border-right: solid 1px #000; height: 0px; font-family: 'Times New Roman';">{description}</td>
                """
            # format item quantity
            # ItemQuantity += (
            #     f"<span >{item['ItemQuantity']}</span> <br>"
            #     if item["ItemQuantity"] != ""
            #     else ""
            # )

        # format total amount
        Subtotal = (
            invoice_data[0]["Subtotal"] if invoice_data[0]["Subtotal"] != "" else ""
        )
        formatSubtotal = f"{Subtotal}.00" if isinstance(Subtotal, int) else Subtotal
        if formatSubtotal != "":
            formatSubtotal = f"{float(formatSubtotal):.2f}"

        # format payments/credits
        payment = (
            invoice_data[0]["AppliedAmount"]
            if invoice_data[0]["AppliedAmount"] != ""
            or invoice_data[0]["AppliedAmount"] != None
            else ""
        )
        payment = float(payment)
        formatPayment = (
            f"{payment:.2f}" if isinstance(payment, (int, float)) else payment
        )

        finalPaymentFormat = (
            f"-${abs(payment):.2f}"
            if isinstance(payment, (int, float)) and payment < 0
            else formatPayment
        )
        if finalPaymentFormat != "":
            finalPaymentFormat = f"${float(formatPayment):.2f}"
        Balance = invoice_data[0]["Balance"] if invoice_data[0]["Balance"] != "" else ""
        formatBalance = f"{Balance}.00" if isinstance(Balance, int) else Balance
        if formatBalance != "":
            formatBalance = f"{float(formatBalance):.2f}"
        html_template = """     
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Invoice</title>
    <style>
      body{{
        font-family: Arial, sans-serif;
        margin: 40px;
      }}
      .header {{
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
      }}
      .header-right {{
        display: flex;
        flex-direction: row;
        gap: 10px;
        justify-content: center;
        align-items: center;
      }}
      .header-left {{
        text-align: center;
        justify-content: center;
      }}
      .header img {{
        width: 115px;
        height: 141px;
      }}
      .invoice-info,
      .billing-info {{
        border-collapse: collapse;
        width: 100%;
        /* margin-bottom: 20px; */
      }}
      .invoice-info th,
      .invoice-info td,
      .billing-info th,
      .billing-info td {{
        border: 1px solid black;
    

        padding: 8px;
      }}
  
      .invoice-text {{
        margin-bottom: 10px;
        text-align: right;
        font-size: 42px;
      }}
      .address-section {{
        display: flex;
        justify-content: space-between;

      
      }}
      .bill-to {{
        background: #b3b0ae9c;
      }}
      .address-section-left {{
        width: 49%;
       
      }}
      .address-section-right {{
        width: 49%;

        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
      }}
      .normal-width {{
        width: 100%;
        border-collapse: collapse;
        border: solid 1px #000;
        margin-bottom: 20px;
      }}

      .bill-address {{
        width: 100%;
        border-collapse: collapse;
      }}
      .bill-to {{
        padding: 10px 20px;
        border: 1px solid #000;
      }}
      .fast-xyz-wrp {{
        padding-left: 48px;
        padding-top: 15px;
      }}
      .sec-td-wrp {{
        padding: 10px 20px;
        border-bottom: 1px solid #000;
        background: #b3b0ae9c;
      }}
      .Project-Address {{
        text-align: center;
        justify-content: center;
        width: 100%;
      }}
      .Project-Address-table {{
        width: 100%;
        border: solid 1px #000;
        border-collapse: collapse;
      }}
      .Project-Address-table td {{
        border-bottom: solid 1px #000;
      }}
      .billing-desc-header {{
        background: #b3b0ae9c;
        text-align: center;
        justify-content: center;
      }}
      .billing-desc {{
        text-align: center;
        justify-content: center;
      }}
      .purchase-desc {{
        text-align: center;
        padding: 8px;
        background: #b3b0ae9c;
      }}
      .purchase-desc-header {{
        text-align: center;
        justify-content: center;
      
        width: 100%;
        border-bottom: solid 1px #000;
        border-right: solid 1px #000;
        border-left: solid 1px #000;
        border-collapse: collapse;
      }}
      .purchase-item {{
        border-top: 1px solid #000;
        height: 540px;
        text-align: start;
        vertical-align: top;
        display: flex;
        flex-direction: column;
      }}
      .purchase-item td:nth-child(even){{
           background-color:#e6e6e6;
      }}
      .footer {{
        border: solid 1px #000;
        border-collapse: collapse;
        width: 100%;
      }}
      .footer td,
      .footer th,
      .footer tr {{
        border: solid 1px #000;
        padding: 20px 5px;
        font-family: "auto";
      }}
      .message {{
        text-align: start;
        font-style: italic;
        font-size: 25px;
        text-align: left;
      }}
      .price {{
        text-align: end;
      }}
      .footer-desc td,
      .footer-desc th,
      .footer-desc tr {{
        border: solid 1px #000;

      
      }}
      .footer-desc {{
        border: solid 1px #000;
        padding: 20px;
        border-collapse: collapse;
        width: 100%;
        text-align: center;
      }}
      .footer-data {{
        padding: 5px;
        background: #b3b0ae9c;
      }}
    </style>
  </head>
  <body>
    <!-- header section -->
    <div class="header">
      <div class="header-right">
        <div>
          <img
            src="https://simplicapital-live-bucket.s3.amazonaws.com/sci-surfaces/logo.jpeg"
            alt="logo"
          />
        </div>
        <div>
          <strong style="font-size: 36px">Surface Center</strong> <br />
          <div style="font-size: 26px">
            12800 Shawnee Mission Pkwy.<br />Shawnee, KS 66216
          </div>
        </div>
      </div>

      <div class="header-left">
        <div class="invoice-text">
          <strong>Invoice</strong>
        </div>
        <table class="invoice-info" style="width: 250px">
          <tr style="background: #b3b0ae9c">
            <td>Date</td>
            <td>Invoice #</td>
          </tr>
          <tr>
            <td>1/16/2024</td>
            <td>24-19136</td>
          </tr>
        </table>
      </div>
    </div>

    <div class="address-section">
      <div class="address-section-left">
        <table class="bill-address">
          <tr>
            <td class="bill-to">Bill To:</td>
          </tr>
          <td class="fast-xyz-wrp">
         {billingAddress}
          </td>
        </table>
      </div>
      <div class="address-section-right">
        <div>
          <table class="normal-width">
            <tr class="sec-tr-wrp">
              <td class="sec-td-wrp">Ship To:</td>
            </tr>
            <tr>
              <td style="padding-bottom: 30px">
                {shippingAddress}
              </td>
            </tr>
          </table>
        </div>
        <div class="Project-Address">
          <table class="Project-Address-table">
            <tr style="background: #b3b0ae9c">
              <td>Project Address</td>
            </tr>
            <tr>
              <td style="padding: 10px">
                34814 - Oral Surgery Kansas Island Modifi
              </td>
            </tr>
          </table>
        </div>
      </div>
    </div>
    <!-- billing address section end -->

    <div class="billing-section">
      <table class="billing-info">
        <tr class="billing-desc-header">
          <td>P.O. Number</td>
          <td>Terms</td>
          <td>Due Date</td>
          <td>Rep</td>
          <td>Via</td>
        </tr>
        <tr class="billing-desc">
          <td>4-362</td>
          <td>Net 30</td>
          <td>2/15/2024</td>
          <td style="color: grey">COM</td>
          <td>Ins KS COM RM**</td>
        </tr>

        <table class="purchase-desc-header">
          <tr>
            <td class="purchase-desc">Description</td>
          </tr>
          <tr class = "purchase-item">
         {desc}
         </tr>

          <table class="footer">
            <tr>
              <th class="message">Thank you for your business</th>
              <th style="width: 22%; text-align: left">Total</th>
              <td class="price">$12,962.49</td>
            </tr>
            <table class="footer-desc">
              <tr>
                <td class="footer-data" style="width: 19%">Phone #</td>
                <td class="footer-data" style="width: 22.3%">E-mail</td>
                <td class="footer-data" style="width: 19.7%">Web Site</td>
                <td
                  class="footer-data"
                  style="
                    font-size: 12px;
                    background-color: transparent;
                    font-weight: bold;
                    width: 20.7%;
                  "
                >
                  Down Payment/Credits
                </td>
                <td
                  class="footer-data"
                  style="
                    width: 15.9%;
                    background-color: transparent;
                    text-align: right;
                  "
                >
                  $0.00
                </td>
              </tr>
              <tr>
                <td style="font-size: 12px">913-422-0500</td>
                <td style="font-size: 12px">rae.selvin@sci-surfaces.com</td>
                <td style="font-size: 12px">www.sci-surfaces.com</td>
                <th style="font-size: 23px; border-right: none">Balance Due</th>
                <td
                  style="
                    border-left: none;
                    padding: 10px 5px;
                    text-align: right;
                  "
                >
                  $1,198.00
                </td>
              </tr>
            </table>
          </table>
        </table>
      </table>
    </div>
  </body>
</html>


""".format(
            date=formatted_date_str,
            refNo=invoice_data[0]["ReferenceNumber"],
            billingAddress=billing_address,
            shippingAddress=shipping_address,
            poNumber=poNo,
            Terms=terms,
            rep=rep,
            Subtotal=formatSubtotal,
            payment=finalPaymentFormat,
            Balance=formatBalance,
            desc=desc,
            paid=paid,
        )
        pdf_name = f"invoice/{fileName}.pdf"
        options = {"page-height": "11in", "page-width": "8.3in"}
        pdfkit.from_string(html_template, pdf_name, options=options)
        print("pdf_name--->", pdf_name)
        return pdf_name

    except Exception as e:
        print("e------>", e)
