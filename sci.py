import pdfkit


html_content = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Invoice</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        margin: 40px;
        box-shadow: none;
      }
      .invoice-box {
        max-width: 900px;
        margin: auto;
        /* padding: 30px; */

        font-size: 16px;
        line-height: 24px;
        /* color: #555; */
      }
      .invoice-box table {
        width: 100%;
        line-height: inherit;
        text-align: left;
        border-collapse: collapse;
      }
      .invoice-box table td {
        padding: 10px;
        vertical-align: top;
        font-size: 14px;
        line-height: 15px;
      }
      .invoice-box table tr td:nth-child(2) {
        text-align: right;
      }
      .invoice-box table tr.top table td {
        padding-bottom: 20px;
      }
      .invoice-box table tr.top table td.title {
        font-size: 16px;
        line-height: 20px;
        color: #333;
        display: flex;
      }
      .invoice-box table tr.information table td {
        padding-bottom: 40px;
        border: 1px solid;
      }

      .invoice-box table tr.heading td {
        background: #eee;
        /* border-bottom: 1px solid #ddd; */
        font-weight: bold;
        border: 1px solid;
        text-align: center;
      }
      .invoice-box table tr.details td {
        padding-bottom: 20px;
      }
      .invoice-box table tr.item td {
        /* border-bottom: 1px solid #eee; */
        height: 550px;
        border: 1px solid;
      }
      .invoice-box table tr.item.last td {
        border-bottom: none;
      }
      .invoice-box table tr.total td:nth-child(2) {
        border-top: 2px solid #eee;
        font-weight: bold;
      }
      .inner_table {
        width: 50%;
        position: relative;
        left: 24%;
        height: fit-content;
        text-align: center;
      }

      .small_table {
        width: 40% !important;
        position: relative;
        left: 60%;
        margin-top: 16px;
        border: 1px solid;
      }
      /* .table_head{
  border: 1px solid;
  justify-content: center;
} */

      .total_data {
        width: 46% !important;
        position: relative;
        left: 54%;
        border: 1px solid;
      }

      /* ------------------updated--css-------------------------- */
      .top_sec {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 15px;
      }

      .top_left_txt_sec {
        width: 40%;
      }

      .top_left_txt_sec p {
        font-family: "Times New Roman", Times, serif;
        color: #000;
        font-size: 16px;
        line-height: 26px;
        margin: 0;
      }

      .top_right_invc_sec {
        width: calc(100% - 68%);
      }
      .top_right_invc_sec h1 {
        font-size: 30px;
        line-height: 30px;
        font-weight: 600;
        text-align: right;
      }
      .top_right_invc_sec table {
        border-collapse: collapse;
        border: 1px solid #000;
      }
      .top_right_invc_sec table th,
      .top_right_invc_sec table td {
        border: 1px solid #000;
        padding: 10px;
        text-align: center !important;
      }

      .sec-td-wrp {
        padding: 10px 20px;
        border-bottom: 1px solid #000;
        /* background: #bfc2c5; */
      }
      .normal-width {
        width: 100%;
        border-collapse: collapse;
        border: solid 1px #000;
        /* margin-bottom: 20px; */
      }

      .address-section-right {
        width: 49%;
        margin: 20px 0px;
        display: flex;
        flex-direction: column;
      }

      .address-section-left {
        width: 49%;
        margin: 20px 30px;
        display: flex;
        flex-direction: column;
      }

      .address-section {
        display: flex;
        justify-content: space-between;
        margin-bottom: 15px;
        /* grid-template-columns: auto auto; */
      }

      .third_sec {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 5px;
      }
      .third_sec_wrp {
        width: 426px;
        display: flex;
        justify-content: space-between;
      }
      .third_sec_info {
        margin-left: 5px;
      }

      .third_sec_info table {
        border-collapse: collapse;
      }
      .third_sec_info table th,
      .third_sec_info table td {
        border: 1px solid #000;
        padding: 10px;
        font-size: 12px;
        display: flex;
        justify-content: center;
        border-top: none;
      }
      .third_sec_info table th {
        border-top: solid 1px #000;
        font-weight: normal;
      }
      /* .forth_sec{margin-bottom: 20px;} */
      .fifth_sec {
        display: flex;
        justify-content: space-between;
      }
      .fifth_sec_left {
        width: 35%;
      }
      .fifth_sec_right {
        width: calc(100% - 60%);
      }
      .fifth_sec_right table {
        border: 1px solid #000;
        font-weight: 600;
      }
      .fifth_sec_right table td {
        line-height: 24px;
      }
      .fifth_sec_right table tr {
        border-bottom: 1px solid #000;
      }
      .fifth_sec_right table tr:last-child {
        border-bottom: none;
      }
      .fifth_sec_left p {
        font-size: 14px;
        line-height: 18px;
        /* color: #555; */
        margin: 4px 0px;
      }
      .address-td{
        padding: 3px !important;
      }

    </style>
  </head>
  <body>
    <div class="invoice-box">
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
                <th>Date</th>
                <th>invoice #</th>
              </tr>
              <tr>
                <td>10/15/2020</td>
                <td>330</td>
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
                  <td style="height: 140px;" class="address-td">
                    Mark Green<br />3821 W. 6th Street<br />Lawrence, KS 66049
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
                  <td style="height: 140px" class="address-td">
                    Mark Green<br />3821 W. 6th Street<br />Lawrence, KS 66049
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <!-- <div class="Project-Address">
        <table class="Project-Address-table">
          <tbody><tr style="background: #bfc2c5">
            <td>Project Address</td>
          </tr>
          <tr>
            <td style="padding: 10px">
              34814 - Oral Surgery Kansas Island Modifi
            </td>
          </tr>
        </tbody></table>
      </div> -->
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
                  <td>10432977</td>
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
                  <td>330</td>
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
                  <td>LC</td>
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
              <td>Description</td>
              <td>Qty</td>

              <td>Amount</td>
            </tr>
            <tr class="item">
              <td style="width: 76%;padding: 3px;">CAB Install HD 410 - HD PO 10432977 Kate Herk</td>
              <td>1</td>
              <td style="text-align: end">$1,469.00</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="fifth_sec">
        <div class="fifth_sec_left">
          <p>
            Please Remit Payment To:<br />
            The Countertop Factory Midwest<br />
            869 S. Route 53 Unit D<br />
            Addison, IL 60101<br />
            Attn: Accounting Dept
          </p>
        </div>
        <div class="fifth_sec_right">
          <table style = 'border-top: none;'>
            <!-- <tr class="total_data"> -->
            <tbody>
              <tr>
                <td >Total</td>
                <td>$1,469.00</td>
              </tr>
              <tr>
                <td>Payments/Credits</td>
                <td>-$1,469.00</td>
              </tr>
              <tr>
                <td style = "font-size: 24px">Balance Due</td>
                <td>$0.00</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </body>
</html>

"""
options = {
     
        'page-height': "11.7in",
        'page-width': "8.3in"
    }
pdfkit.from_string(html_content, "output1.pdf")
print("PDF generated successfully!")
