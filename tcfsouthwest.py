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
            Key=f"simplicapital/cdata/tcfsouthwest/InvoiceLineItems/{fileName}",
        )
        #  read and decode data from S3 bucket
        file_content = response["Body"].read().decode("utf-8")
        # parse the data into JSON format
        data = json.loads(file_content)

        # return the data
        return data
    except Exception as error:
        print("Error---->", error)


def processData(event, flag=0, skip=0, invoiceName=None):
    print("invoicename:--->", invoiceName)
    # get data from S3 bucket
    # data = getDataFromS3(event["file_name"])
    if invoiceName is None:
        invoiceName = []
    # get data from database
    invoices = findInvoiceByReferenceNumber(
        event["tenant"], event["invoice_ref_no"], skip
    )
    data = list(invoices)

    # store matched invoice
    matched_invoice = []
    # map the data
    for refNo in data:

        # find a particular invoice
        if (
            event["invoice_ref_no"] == refNo["ReferenceNumber"]
            and refNo["ItemIsGetPrintItemsInGroup"] is None
            or refNo["ItemIsGetPrintItemsInGroup"] == None
        ):
            # push the invoice into a array
            matched_invoice.append(refNo)
    name = f'{event["invoice_ref_no"]}_{flag}' if flag != 0 else event["invoice_ref_no"]

    # sent data to generateHtmlToPdf
    res = generateHtmlToPdf(matched_invoice, event, name)
    if invoiceName != None:
        invoiceName.append(res)

    if len(data) > 0:
        count = flag + 1
        print("hit recursive---->")
        skip_data = skip + 30
        processData(event, count, skip_data, invoiceName)

    return invoiceName


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
        # is paid format
        if invoice_data[0]["IsPaid"] == "true" or invoice_data[0]["IsPaid"] == True:

            paidDate = findPaidDate(event["tenant"], event["invoice_ref_no"])
            paidDate = paidDate["dtCollection"]
            paidDate = datetime.strptime(paidDate, "%Y-%m-%d")
            paidDate = paidDate.strftime("%m/%d/%Y")
            paid = f"""
          <div style= "position:absolute;z-index:1;top:89px;left:354px;">
        
            <img src= "https://allassets.s3.amazonaws.com/invoice-materials/paid.png" style="width:180px;position:relative"/>
            <span style= "font-size:24px;font-weight: bold;transform:rotate(-24deg);position:absolute;right:-6px;top:80px">{paidDate}<span>
            
          </div>
          """
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
            else ""
        )
        ShippingState = (
            invoice_data[0]["ShippingState"] + ","
            if invoice_data[0]["ShippingState"] != ""
            else ""
        )
        ShippingPostalCode = (
            invoice_data[0]["ShippingPostalCode"]
            if invoice_data[0]["ShippingPostalCode"] != ""
            else ""
        )

        shipping_address = f"""{ShippingLine1}{ShippingLine2}{ShippingLine3}{ShippingLine4}{ShippingLine5}{ShippingCity}{ShippingState}{ShippingPostalCode}"""

        # format P.O.No.
        poNo = invoice_data[0]["PONumber"] if invoice_data[0]["PONumber"] != "" else ""
        if len(poNo) > 17:
            poNo = f"{poNo[:18]}..."
        # format Terms
        terms = invoice_data[0]["Terms"] if invoice_data[0]["Terms"] != "" else ""
        # format SalesRep
        rep = invoice_data[0]["SalesRep"] if invoice_data[0]["SalesRep"] != "" else ""

        # format ItemDescription & amount

        formatAmount = ""
        ItemQuantity = ""
        desc = ""
        for index, item in enumerate(invoice_data):

            # format item amount
            amount = item["ItemAmount"] if item["ItemAmount"] != "" else ""
            amount = amount if amount != None else ""
            # format quantity
            ItemQuantity = item["ItemQuantity"] if item["ItemQuantity"] != "" else ""
            ItemQuantity = ItemQuantity if ItemQuantity != None else ""
            # format description

            formatAmount = f"{amount}.00" if isinstance(amount, int) else amount
            if formatAmount != "":
                formatAmount = f"{float(formatAmount):.2f}"
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
            desc += f"""<tr class="desc-tr">
                  <td style="width: 76%;border-right: solid 1px #000; height: 0px; font-family: 'Times New Roman';">{description}</td>
                  <td style="width: 7%;border-right: solid 1px #000;height: 0px;font-family: 'Times New Roman';">{ItemQuantity}</td>
                  <td style="text-align: end; font-family: 'Times New Roman';">{formatAmount}</td>
                </tr>"""
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
@font-face{{
    font-family: Lintsec;
    src: url(fonts/Lintsec.ttf);
}}

  body {{
    font-family: Arial, sans-serif;
    margin: 50px;
    box-shadow: none;
  }}
  .invoice-box {{
    max-width: 900px;
    margin: auto;
    font-size: 16px;
    line-height: 24px;
    position: relative;
  }}
  .invoice-box table {{
    width: 100%;
    line-height: inherit;
    text-align: left;
    border-collapse: collapse;
  }}
  .invoice-box table td {{
    padding: 10px;
    vertical-align: top;
    font-size: 14px;
    line-height: 15px;
  }}
  .invoice-box table tr td:nth-child(2) {{
    text-align: right;
  }}
  .invoice-box table tr.top table td {{
    padding-bottom: 20px;
  }}
  .invoice-box table tr.top table td.title {{
    font-size: 16px;
    line-height: 20px;
    color: #333;
    display: flex;
  }}
  .invoice-box table tr.information table td {{
    padding-bottom: 40px;
    border: 1px solid #000;
  }}
  .invoice-box table tr.heading td {{
    background: #e6e6e6;
    
    border: 1px solid #000;
    text-align: center;
  }}
  .invoice-box table tr.details td {{
    padding-bottom: 20px;
  }}
  .invoice-box table tr.item td {{
    min-height: 550px;
    border: 1px solid #000;
  }}
  .invoice-box table tr.item.last td {{
    border-bottom: none;
  }}
  .invoice-box table tr.total td:nth-child(2) {{
    border-top: 1px solid #eee;
    font-weight: bold;
  }}
  .inner_table {{
    width: 50%;
    position: relative;
    left: 24%;
    height: fit-content;
    text-align: center;
  }}
  .small_table {{
    width: 40% !important;
    position: relative;
    left: 60%;
    margin-top: 16px;
    border: 1px solid;
  }}
  .total_data {{
    width: 46% !important;
    position: relative;
    left: 54%;
    border: 1px solid;
  }}
  .top_sec {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 13px;
  }}
 .top_left_txt_sec {{
    width: 80%;
}}
  .top_left_txt_sec p {{
    font-family: "Times New Roman", Times, serif;
    color: #000;
    font-size: 18px;
    line-height: 26px;
    margin: 0;
  }}
  .top_right_invc_sec {{
    width: calc(100% - 68%);
  }}
  .top_right_invc_sec h1 {{
    font-size: 36px;
    margin: 15px 0px;
    font-weight: Bold;
    text-align: right;
   
  }}
  .top_right_invc_sec table {{
    border-collapse: collapse;
    border: 1px solid #000;
  }}
  .top_right_invc_sec table th,
  .top_right_invc_sec table td {{
    border: 1px solid #000;
    padding: 10px;
    text-align: center !important;
  }}
  .sec-td-wrp {{
    padding: 10px 20px;
    border-bottom: 1px solid #000;
  }}
  .normal-width {{
    width: 100%;
    border-collapse: collapse;
    border: solid 1px #000;
  }}
  .address-section-right {{
    width: 49%;
    margin: 20px 0px;
    display: flex;
    flex-direction: column;
  }}
  .address-section-left {{
    width: 49%;
    margin: 20px 30px;
    display: flex;
    flex-direction: column;
  }}
  .address-section {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
  }}
  .third_sec {{
    display: flex;
    justify-content: flex-end;
    margin: 0px -3px 5px 0px;
  }}
  .third_sec_wrp {{
    width: 410px;
    display: flex;
    justify-content: center;
    gap: 10px;
  }}
  .third_sec_info{{
    margin-left: 5px;
  }}

  .third_sec_info table {{
    border-collapse: collapse;
  }}
  .third_sec_info table th,
  .third_sec_info table td {{
    border: 1px solid #000;
    padding: 10px;
    font-size: 12px;
    display: flex;
    justify-content: center;
    border-top: none;
  }}
  .third_sec_info table th {{
    border-top: solid 1px #000;
    font-weight: normal;
  }}
  .fifth_sec {{
    display: flex;
    justify-content: space-between;
  }}
  .fifth_sec_left {{
    width: 35%;
  }}
  .fifth_sec_right {{
    width: calc(100% - 62%);
  }}
  .fifth_sec_right table {{
    border: 1px solid #000;
    
  }}
  .fifth_sec_right table td {{
    line-height: 24px;
  }}
  .fifth_sec_right table tr {{
    border-bottom: 1px solid #000;
  }}
  .fifth_sec_right table tr:last-child {{
    border-bottom: none;
  }}
  .fifth_sec_left p {{
    font-size: 13px;
    line-height: 18px;
    /* color: #555; */
    margin: 4px 0px;
    font-family: "Times New Roman";
}}
   .desc-table{{
        border: solid 1px #000;
        border-collapse: collapse;
        min-height: 550px;
        max-height: 550px;

      }}
      .desc-tr:nth-child(even){{
        background-color:#e6e6e6;
       
      }}
      .desc-tr td{{
        padding: 1px !important;
        height: 10px;
        line-height: 16px !important;
        font-size: 10px;
        text-align: start;
      }}
      .desc-tr:last-child td{{
        height: auto !important;
        color: #eee;
      }}
      .address-td{{
        padding: 2px !important;
        line-height: 18px !important;
      }}
      

</style>
</head>
<body>
<div class="invoice-box">
{paid}
<div class="top_sec">
  <div class="top_left_txt_sec">
    <p>
      The Countertop Factory Southwest <br />5970 South Palo Verde Road<br />
      Tucson, AZ 85706
      <br />Office: 630-458-0474 Option 6 <br />Email:
      accounting@tcfmidwest.com
    </p>
  </div>
  <div class="top_right_invc_sec">
    <h1>Invoice</h1>
    <table>
      <tbody>
        <tr>
          <td style="
    padding: 10px 0px;
">Date</td>
          <td style="
    padding: 10px 0px;
">Invoice #</td>
        </tr>
        <tr>
          <td style="
    padding: 10px 0px;
">{date}</td>
          <td style="
    padding: 10px 0px;
">{refNo}</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<div class="second_sec address-section">
  <div class="address-section-left">
    <div>
      <table class="normal-width">
        <tbody>
          <tr class="sec-tr-wrp">
            <td class="sec-td-wrp">Bill To:</td>
          </tr>
          <tr>
            <td style="height: 142px;font-family:'Times New Roman';" class="address-td">
             {billingAddress}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <div class="address-section-right">
    <div>
      <table class="normal-width">
        <tbody>
          <tr class="sec-tr-wrp">
            <td class="sec-td-wrp">Ship To:</td>
          </tr>
          <tr>
            <td style="height: 142px;font-family:'Times New Roman';" class="address-td">
             {shippingAddress}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<div class="third_sec">
  <div class="third_sec_wrp">
    <div class="third_sec_info" style="width: 35%">
      <table>
        <tbody>
          <tr>
            <th>P.O. No.</th>
          </tr>
          <tr>
            <td class = "po-number" style="
    min-height: 15px;">{poNumber}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="third_sec_info" style="width: 35%">
      <table>
        <tbody>
          <tr>
            <th>Terms</th>
          </tr>
          <tr>
            <td style="
    min-height: 15px;">{Terms}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="third_sec_info" style="width: 25%">
      <table>
        <tbody>
          <tr>
            <th>Rep</th>
          </tr>
          <tr>
            <td style="
    min-height: 15px;">{rep}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<div class="forth_sec">
  <table>
    <tbody>
      <tr class="heading">
        <td style="width: 78%;">Description</td>
        <td style="width: 9%;">Qty</td>
        <td>Amount</td>
      </tr>
      
    <tr>
     <tr class="item">
 
          <table style="width: 100%;border: solid 1px #000;height: 570px;" class= "desc-table">
          {desc}
               
         
                <tr>
                  <td style="width: 78%;border-right: solid 1px #000; "></td>
                  <td style="width: 9%;border-right: solid 1px #000;"></td>
                  <td style="text-align: end"></td>
                </tr>
              </table>
        </tr>
    </tr>
    </tbody>
  </table>
</div>

<div class="fifth_sec">
  <div class="fifth_sec_left">
    <p>
      Please Remit Payment To:<br />The Countertop Factory Midwest<br />869 S. Route 53 Unit D<br />Addison, IL 60101<br />Attn: Accounting Dept
    </p>
  </div>
  <div class="fifth_sec_right">
    <table style='border-top: none;'>
      <tbody>
        <tr style= "height:55px">
          <td style="font-weight: 600;font-size:18px;padding-top:15px;">Total</td>
          <td style="font-weight: normal; padding:22px 5px 0px 0px;font-family: 'Times New Roman';">${Subtotal}</td>
        </tr>
        <tr>
          <td style="font-weight: 600;font-size:18px;">Payments/Credits</td>
          <td style="font-weight: normal; padding:19px 5px 0px 0px;font-family: 'Times New Roman';">{payment}</td>
        </tr>
        <tr>
          <td style="font-size: 24px; font-weight: 600;">Balance Due</td>
          <td style="font-weight: normal;padding:19px 5px 0px 0px;font-family: 'Times New Roman';">${Balance}</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
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
        print("html---->", html_template)
        pdf_name = f"invoice/{fileName}.pdf"
        options = {"page-height": "11in", "page-width": "8.3in"}
        pdfkit.from_string(html_template, pdf_name, options=options)
        print("pdf_name--->", pdf_name)
        return pdf_name

    except Exception as e:
        print("e------>", e)
