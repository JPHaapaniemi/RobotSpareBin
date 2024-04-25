from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Indistries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the ordered robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=10,
    )
    open_robot_order_website()
    close_annoying_modal()
    loop_the_orders()
    archive_receipts()


def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """Downloads csv file from given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    orders = library.read_table_from_csv("orders.csv", columns=["Order number","Head","Body","Legs","Address"])
    return(orders)

def close_annoying_modal():
    """Closes the annoying modal popup"""
    page = browser.page()
    page.click("text=OK")

def loop_the_orders():
    """Loops the orders and calls fill_the_form with every row passed as a variable"""
    orders = get_orders()
    for row in orders:
        fill_the_form(row)

def fill_the_form(order):
    """Fills in the form for ordering the robot"""
    page = browser.page()
    page.select_option("#head", order["Head"])
    x = str(order["Body"])
    page.click(f"#id-body-{x}")
    page.get_by_placeholder("Enter the part number for the legs").fill(order["Legs"])
    page.fill("#address", order["Address"])
    page.click("button:text('Preview')")
    handle_ordering(order["Order number"])

def handle_ordering(order_number):
    """Presses order button and handles retry"""
    page = browser.page()
    while True:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:
            store_receipt_as_pdf(order_number)
            screenshot_robot(order_number)
            screenshot = (f"output/screenshots/screenshot_{order_number}.png")
            pdf_file = (f"output/receipts/receipt_{order_number}.pdf")
            print (screenshot + pdf_file)
            embed_screenshot_to_receipt(screenshot, pdf_file)
            order_another_bot()
            close_annoying_modal()
            break

def order_another_bot():
    """Presses the Order another robot button on demand"""
    page = browser.page()
    page.click("#order-another")

def store_receipt_as_pdf(order_number):
    """Store order receipt as pdf"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(receipt_html, f"output/receipts/receipt_{order_number}.pdf")

def screenshot_robot(order_number):
    """Take a screenshot of the robot"""
    page = browser.page()
    page.query_selector("#robot-preview-image").screenshot(path=f"output/screenshots/screenshot_{order_number}.png")

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Add the screenshot into the order pdf"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(
        image_path=screenshot,
        source_path=pdf_file,
        output_path=pdf_file,
    )

def archive_receipts():
    """Compress the receipts into a zip-file"""
    arch = Archive()
    arch.archive_folder_with_zip("output/receipts", "output/receipts.zip")