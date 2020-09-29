from tkinter import *
import smtplib
from bs4 import BeautifulSoup
import requests
import sys
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import random
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
import threading
import os
import re
import hashlib, binascii
from pymongo import MongoClient

# los.system('sudo apt install python3-pip')
# os.system('pip3 install lxml')
# os.system('pip3 install gspread')

global logged_in
global line1
line1=""


##### Database connecrion #####
# scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# credentials = ServiceAccountCredentials.from_json_keyfile_name('stockgetter-02bc755504f9.json', scope)
# gc = gspread.authorize(credentials)

# usersSheet = gc.open('StockGetter').sheet1
# followSheet = gc.open('StockGetter-Follow').sheet1

client=MongoClient("mongodb+srv://db_user:4713@cluster0.x4gf7.mongodb.net/Stocker?retryWrites=true&w=majority")
# client=MongoClient("mongodb+srv://db_user:4713@cluster0.x4gf7.mongodb.net/Stocker?retryWrites=true&w=majority")
db=client.get_database('Stocker')
Users=db.Users
Followers=db.Followers

###############################

stockName = ""
limitPrice = 0
gmail_user = 'mailchecker47@gmail.com'
gmail_password = 'fsnfihvyjocfxxcx'

screenBackground = '#6d9eed'

buttonGrayBackground = "#B2BABB"
labelFont = ('David', 16)
labelFontBold = ('David', 16, 'bold')
logged_in = 0
userName = ""
userMail = ""



# logRegWindow=""
# registerButton=""

######### security ###########
def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')
 
def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

####################


def create_pop_window(title, message, size, button1_text, button2_text, button2_func):
    """A function that creates generic pop-up window, with the corresponding fields:
	title, the message string, window size and its buttons. """
    pop_window = Toplevel()
    pop_window.resizable(0, 0)
    icon = PhotoImage(file='icon.png')
    pop_window.iconphoto(False, icon)
    pop_window.title(title)
    l = Label(pop_window, font=labelFont, text=message, justify='center')
    pop_window.geometry(size)
    l.pack(side="top")
    if (button2_text != ""):
        b2 = Button(pop_window, text=button2_text, command=button2_func)
        b2.pack()
    b1 = Button(pop_window, text=button1_text, command=pop_window.destroy)
    b1.pack()

def start_timer(user_name_to_check,user_mail_to_check,password_to_check):
	# usersSheet.append_row([user_name_to_check, user_mail_to_check, password_to_check,"NO"])
    Users.insert_one({'Username':user_name_to_check , 'Mail':user_mail_to_check,'Password': hash_password(password_to_check),'Verified':"NO"})
    time.sleep(60)

	# userCell=usersSheet.find(user_mail_to_check)
    userDocument= Users.find_one({'Username':user_mail_to_check})

    

	# if(usersSheet.cell(userCell.row , userCell.col+2 ).value == "NO"):
	# 	usersSheet.delete_rows(userCell.row)
	# 	print("user deleted")
	# 	create_pop_window("Email was not verified", "You didn't verified your email whitin 60 seconds, try again\n", "460x120", "Try again",
 #                          "", "")
	# else:
	# 	print("got to the else")

    if(userDocument['Verified'] == "NO"):
        Users.delete_one(userDocument)
        print("user deleted")
        create_pop_window("Email was not verified", "You didn't verified your email whitin 60 seconds, try again\n", "460x120", "Try again",
                          "", "")
    else:
        print("got to the else")


def send_confirmation_code(userMail,randomForConfirmaionMail):
    """A function used for send confirmation mail to the user un order to verify her/his email address.
	pop ups an error window if failed to send the mail.
	Parameters
    ----------
    randomForConfirmaionMail: the random number(between 0-100000) created for registration

    """
    # print(randomForConfirmaionMail)
    # userMail = userMailEntry.get()
    if ('@' not in userMail):
        create_pop_window('Error: wrong email', "You didn't entered a valid email\n", '330x120', 'Try again', "", "")

    else:
        # sent_from = "STOCKER"
        # to = userMail
        msg = MIMEText(
            """Hey! I am glad that you chose our program!\n Here is your confirmation code for registration: \n\n%s\n\n
            	Please type / paste it in the "Confirmation code" place and click "Register".\nWelcome abord! :) """
            	 % (randomForConfirmaionMail))
        msg['From'] = "STOCKER"
        msg['Subject'] = 'STOCKER - Confirmation code'
        msg['To'] = userMail
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_password)
            server.sendmail("STOCKER", userMail, msg.as_string())
            server.close()
            print ('Confirmation mail sent!')
        except:
            create_pop_window("Error",
                              "Something went wrong.\nMaybe you typed wrong mail or don't have internet connection",
                              '530x200', 'ok', "", "")



def RegistrationSelected(logRegWindow,registerButton, userNameEntry,passwordEntry):
	"""A function used for before sign up the user,after "register" button was selected,
	shows more entries needed to be fiil by the user in order to register 
	"""
	emailLabel = Label(logRegWindow, text='EMAIL: ', font=labelFont)
	repeatPasswordLabel = Label(logRegWindow, text='Reapet password: ', font=labelFont)
	userMailEntry = Entry(logRegWindow, width=28)
	reapetPasswordEntry = Entry(logRegWindow, show="*", width=28)
	emailLabel.grid(row=1, column=0)
	userMailEntry.grid(row=1, column=1)
	repeatPasswordLabel.grid(row=3, column=0)
	reapetPasswordEntry.grid(row=3, column=1)
	registerButton.config(text="Register")
	logRegWindow.geometry('470x250')
	registerButton.config(font=("David", 16, "bold"))
	registerButton.config(command=lambda:[try_register(logRegWindow, registerButton,userNameEntry,userMailEntry,passwordEntry,reapetPasswordEntry)]) 


def try_register(logRegWindow,registerButton,userNameEntry,userMailEntry,passwordEntry,reapetPasswordEntry):
    """A function used to sign up the user, checks all the fields are ok(same password, etc.)
	and add the user to the users table on the database. Pop ups an error massege if failed
	Parameters
    ---------- 
	randomForConfirmaionMail: the random confirmation code (betwwen 0-100000),
	used to verify the users mail (check if the typed code equals the randomly generated one).
    """


    randomForConfirmaionMail = int((random.random()) * 1000000)


    mailOk = 1
    nameOk = 1
    user_name_to_check = userNameEntry.get()
    user_mail_to_check = userMailEntry.get()
    password_to_check = passwordEntry.get()
    repeat_password_to_check = reapetPasswordEntry.get()

   
    print(randomForConfirmaionMail)


    can_register = 1
    errorMsg = "Somthing went wrong:"
    mistake_counter=0


    # list_of_cells_with_same_username = usersSheet.findall(user_name_to_check)
    # for cell in list_of_cells_with_same_username:
    #     if (cell.col == 1):
    #         nameOk = 0
    #         break
    if(Users.count_documents({'Username':user_name_to_check})>0):
        nameOk = 0

    if (nameOk == 0):
        can_register = 0
        errorMsg = errorMsg + "\nUser name already taken"
        mistake_counter=mistake_counter+1

    # list_of_cells_with_same_mail = usersSheet.findall(user_mail_to_check)
    # for cell in list_of_cells_with_same_mail:
    #     if cell.col == 2:
    #         mailOk = 0
    #         break

    if(Users.count_documents({'Mail':user_mail_to_check})>0):
        mailOk = 0 

    if (mailOk == 0):
        can_register = 0
        errorMsg = errorMsg + "\nThis mail already registrered to our service."
        mistake_counter=mistake_counter+1


    if (repeat_password_to_check != password_to_check):
        can_register = 0
        errorMsg = errorMsg + "\nPasswords does not match."
        mistake_counter=mistake_counter+1

    if (len(password_to_check) <= 3):
        can_register = 0
        errorMsg = errorMsg + "\nPasswords size should be at least 4 ."
        mistake_counter=mistake_counter+1

    if (can_register == 0):
        create_pop_window('Registration Error', errorMsg, '530x'+str(50+(mistake_counter+1)*40), "Try again", "", "")


    else:
    	codeLabel = Label(logRegWindow, text='Confirmation code: ', font=labelFont)
    	confirmationCodeEntry = Entry(logRegWindow, width=28)

    	codeLabel.grid(row=4, column=0)
    	confirmationCodeEntry.grid(row=4, column=1)
    	send_confirmation_code(user_mail_to_check,randomForConfirmaionMail)
    	# global registerButton
    	registerButton.config(command=lambda: add_user_to_db( logRegWindow, registerButton,user_name_to_check, user_mail_to_check, password_to_check,str(confirmationCodeEntry.get()),str(randomForConfirmaionMail),userNameEntry,userMailEntry,passwordEntry,reapetPasswordEntry))
    	registerButton.config(text="Confirm")
    	varificationThread = threading.Thread(target=start_timer,args=([user_name_to_check,user_mail_to_check,password_to_check]), daemon=True)

    	varificationThread.start()


def add_user_to_db( logRegWindow,registerButton, user_name_to_check, user_mail_to_check, password_to_check,user_confirmation_code,randomForConfirmaionMail_str,userNameEntry,userMailEntry,passwordEntry,reapetPasswordEntry):
    if (user_confirmation_code != randomForConfirmaionMail_str):
        
        create_pop_window('Registration Error', "Wrong confirmation code, check your mail.\n", '370x110', "Try again", "", "")
    else:
        registerButton.config(command=lambda: try_register(logRegWindow,registerButton,userNameEntry,userMailEntry,passwordEntry,reapetPasswordEntry))
        registerButton.config(text="Register")
        # # usersSheet.append_row([user_name_to_check, user_mail_to_check, password_to_check,""])
        # userCell=usersSheet.find(user_name_to_check)
        # usersSheet.update_cell(userCell.row, userCell.col + 3, 'YES')
        
        verify_update={'Verified':"YES"}
        Users.update_one({'Username':user_name_to_check},{'$set':verify_update})


        create_pop_window('Welcome aboard!', "Register successfully !", '360x120', "Close", 'Login', lambda: login(logRegWindow, user_name_to_check,password_to_check))


def delete_selected_stocks(listbox,userMail):
    """A function used for delete the stocks that the user selected on the list
	Parameters
    ----------
    listbox: the stocks list shown to the user.
	  """
    stopped = ""
    counter=0
    # follow_list = followSheet.findall(userMail)
    # follow_list=list(Followers.find_one('Mail':userMail))

    selected = listbox.curselection()

    for index in selected[::-1]:
        stock_to_delete_from_list = listbox.get(index, index)[0]
        stock_to_delete_from_list = stock_to_delete_from_list[0:stock_to_delete_from_list.rfind(" --> ")]
        listbox.delete(index)
        Followers.delete_one({'Mail':userMail, 'Stock': stock_to_delete_from_list })







    # for index in selected[::-1]:
    #     for followed in follow_list:
    #         stock_to_delete_from_sheet = followSheet.cell(followed.row, followed.col + 1).value
    #         stock_to_delete_from_list = listbox.get(index, index)[0]
    #         stock_to_delete_from_list = stock_to_delete_from_list[0:stock_to_delete_from_list.rfind(" --> ")]
    #         if (stock_to_delete_from_sheet == stock_to_delete_from_list):
    #             stopped = stopped + "\n" + stock_to_delete_from_sheet
    #             followSheet.delete_rows(followed.row)
    #             listbox.delete(index)
    #             # print(stock_to_delete_from_sheet)
    #             # print(stock_to_delete_from_list)
    #             counter=counter+1
    #             break

    # if (stopped != ""):
    #     create_pop_window("Stop scanning", "You stopped scanning " + stopped + "\n", '420x'+str(counter*40+55), "Close", "", "")


def set_stocks_list(listbox,userMail):
    """ A function used to set the users stocks list when starting the software.
	Gets the users stocks from the database and put it in listbox.
	Parameters
    ----------
	listbox: the stocks list shown to the user
	"""
    # follow_list = followSheet.findall(userMail)
    # for followed in follow_list:
    #  if(followSheet.cell(followed.row, followed.col + 4).value == "NO"):	
    #     listbox.insert(END,
    #                    followSheet.cell(followed.row, followed.col + 1).value + " --> " + followSheet.cell(followed.row,followed.col + 2).value)
    
    follow_list=list(Followers.find({'Mail':userMail,'Sent':"NO"}))
    for i in range (len(follow_list)):
        stockDocument=follow_list[i]
        listbox.insert(END,stockDocument['Stock']+ " --> " + str(stockDocument['Price']))                                                                                              


def main_window(userName,userMail):
    """ A function used to create the main window of the software.
    Contains 5 frames in order to manage the content in the window.
	Run the mainThread - in order to check the stocks on a background process. 
    Parameters
    ----------
    userName: The user's name to be wriiten in the window and to be used by other functions
    userMail: The user's mail to be wriiten in the window and to be used by other functions

    """

    master = Tk(className='Stock assistent')
    master.resizable(0, 0)
    icon = PhotoImage(file='icon.png')
    master.iconphoto(False, icon)
    master.geometry('820x530')
    master['bg'] = screenBackground
    master.title('Strategy window')

    ### user deatails ###
    user_details_frame = Frame(master, relief="solid")
    user_details_frame.grid(column=0, row=0, sticky=W)
    user_details_frame['bg'] = screenBackground
    Label(user_details_frame, text='User Name :', relief="groove",width=12, font=labelFontBold, background=buttonGrayBackground).grid(
        column=0, row=0)
    Label(user_details_frame, text='Email :', relief="groove", width=12,font=labelFontBold, background=buttonGrayBackground).grid(
        column=0, row=1)

    # global userName
    # global userMail
    userNameLabel = Label(user_details_frame, text=userName, font=labelFontBold, relief="groove",
                          background=buttonGrayBackground).grid(column=1, row=0, padx=70)
    userMailLabel = Label(user_details_frame, text=userMail, font=labelFontBold, relief="groove",
                          background=buttonGrayBackground).grid(column=1, row=1, padx=70)
    log_out_button = Button(user_details_frame, font=labelFont, text='log out', background=buttonGrayBackground,width=12,relief="groove",
                            command=lambda:[ ask_log_out(master,userName,userMail)]).grid(column=2, row=0)
    sign_out_button = Button(user_details_frame, font=labelFont, text='sign out', background=buttonGrayBackground,width=12,relief="groove",
                             command=lambda: [ ask_sign_out(master,userName,userMail)]).grid(column=2, row=1)

    ### stock details ###
    search_frame = Frame(master)
    search_frame.grid(column=0, row=1, sticky=W)
    search_frame['bg'] = screenBackground

    LabelStock = Label(search_frame, font=labelFont, text="Stock's symbol / name to follow", height=2,background=screenBackground)
    LabelStock.grid(column=0, row=0, sticky=W)

    stockNameEntry = Entry(search_frame, font=labelFont)
    stockNameEntry.grid(column=1, row=0)

    search_button = Button(search_frame, text="search", font=labelFont, background="#00ff00",
                           command=lambda: [searchClicked(master,stocks_list,str(stockNameEntry.get()),userName,userMail)]).grid(column=2, row=0, padx=30)

    ### stock's list frame ###

    stocks_list_frame = Frame(master, bg=screenBackground)
    stocks_list_frame.grid(column=0, row=4)

    stocks_list = Listbox(stocks_list_frame, bg='#FFFFFF', selectmode="multiple", bd=2, font=labelFont)
    set_stocks_list(stocks_list,userMail)

    scroll_bar = Scrollbar(stocks_list_frame)

    stocks_list.config(yscrollcommand=scroll_bar.set)
    scroll_bar.config(command=stocks_list.yview)
    delete_button = Button(stocks_list_frame, text="Stop follow and delete selected", font=labelFont,
                           background="#ff0000", command=lambda: delete_selected_stocks(stocks_list,userMail))

    delete_button.pack(side=BOTTOM)

    list_title = Label(stocks_list_frame, text="My stocks list( stock name --> my price ) ", borderwidth=1,
                       relief="ridge", font=labelFontBold)
    list_title.pack(side=TOP)
    stocks_list.pack(side=LEFT, fill=BOTH, expand=1)

    scroll_bar.pack(side=RIGHT, fill=Y)

    mainThread = threading.Thread(target=check_stocks,args=([userMail,stocks_list]), daemon=True)

    mainThread.start()

    master.mainloop()

    sys.exit()


def login(logRegWindow,user_name_to_check,password_to_check):
    """A function used to log in the user to the service. Check if the username and password equals to the ones in the database.
    If so , log in the user and open the main window.
    If fails, pop ups an error message.

    """
    nameOk = 0
    can_login = 1
    errorMsg = ""

    if(Users.count_documents({'Username':user_name_to_check})==1):
        nameOk=1

    # list_of_cells_with_same_username = usersSheet.findall(user_name_to_check)
    # for cell in list_of_cells_with_same_username:
    #     if cell.col == 1:
    #         nameOk = 1

    if (nameOk == 0):
        can_login = 0
        errorMsg = errorMsg + "Something Went wrong, check username and password"


    if(nameOk == 1 and verify_password(Users.find_one({'Username':user_name_to_check})['Password'],password_to_check)==False) : 

    # if nameOk == 1 and str(password_to_check) != str(usersSheet.cell(usersSheet.find(user_name_to_check).row,
    #                                                                  usersSheet.find(
    #                                                                          user_name_to_check).col + 2).value):
        print("hey")
        can_login = 0
        errorMsg = errorMsg + "Something Went wrong, check username and password"
    if (can_login == 0):
        create_pop_window("Login Error", errorMsg, '520x80', "Try again", "", "")


    else:
        global  logged_in
        logged_in = 1
        logRegWindow.destroy()
        userName = user_name_to_check
        # userMail = usersSheet.cell(usersSheet.find(user_name_to_check).row,
        #                            usersSheet.find(user_name_to_check).col + 1).value
        userMail=Users.find_one({'Username':user_name_to_check})['Mail']
        

        main_window(userName,userMail )


def getStockName(stock_name_to_search,alsoGetPrice):
    """ A function used to get the searched stock full name
    
    Parameters
    ----------
    stock_name_to_search: The stock's name entered by the user
    alsoGetPrice: 1 if the price is required, else 0.
    
    Returns
    ----------
    A string with the stock name and price if required.
    """
    url = "https://finance.yahoo.com/lookup?s={}".format(stock_name_to_search)
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'lxml')
    stockName = soup.find('td', attrs={"data-reactid": "58"})  # 57+8*n
    if (stock_name_to_search == "" or stockName is None):
        return ""
    else:
        currentPrice = soup.find('td', attrs={"data-reactid": "59"})  # 59+8*n
        if (alsoGetPrice == 0):
            return (stockName.text)
        else:
            cur_price_text = currentPrice.text
            return (stockName.text + " stock: " + cur_price_text[: cur_price_text.find('.') + 3])

def send_stock_update_mail(stockName, limitPrice,userMail):
    """ A function used to send an email to the user when one or more
    of his / her stocks got to his / her limit.
    
    Parameters
    ----------
    stockName: The stocks full name of the one the user search for.
    limitPrice: The user limit to be notified when over(below or above),
    defined by the user.

	Sending the email, if fails popups an error window. 
    """
    sent_from = "STOCKER"
    to = userMail
    msg = MIMEText('Hey, whats up?\nYour stock %s got to your limit %s in the last minute!' % (stockName, limitPrice))
    msg['Subject'] = 'Stock updating - got to your limit'
    msg['From'] = "STOCKER"
    msg['To'] = userMail

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, userMail, msg.as_string())
        server.close()
        print ('Email sent!')

    except:
        print ('Something went wrong...')


def check_stocks(userMail,listbox):
    """ A function used to check if each stock from the user's
     list got to his/her limit price.
    Parameters
    ----------
    userMail: The user's mail - used to get his stock's from the database.
	
	Working with a single thread that check the prices every minute
	while the user still logged in.  
    """
    global logged_in
    while (logged_in==1):
        # follow_list = followSheet.findall(userMail)

        stocks_to_check=list(Followers.find({'Mail':userMail,'Sent':"NO" }))
        # print(len(follow_list))
        for followed in stocks_to_check:
            stockName = followed['Stock']
            # print(stockName)
            limitPrice = followed['Price']
            # print(limitPrice)

            over = followed['Over']
            url = "https://finance.yahoo.com/lookup?s={}".format(stockName)
            source = requests.get(url).text
            soup = BeautifulSoup(source, 'lxml')
            currentPrice = soup.find('td', attrs={"data-reactid": "59"})  # 59+8*n
            sent_update=({'Sent':"YES"})

            if (over == '1'):
                if (float(without_comma(currentPrice.text)) <= float(limitPrice)):
                    send_stock_update_mail(stockName, limitPrice,userMail)

                    # followSheet.update_cell(followed.row, followed.col + 4, 'YES')
                    Followers.update_one({'Username':followed['Username'], 'Stock':followed['Stock']},{'$set':sent_update})

                    for i in range(listbox.size() - 1, -1, -1):
                        stock_name_to_check = listbox.get(i, i)[0]
                        if (stock_name_to_check[0:stock_name_to_check.rfind(" --> ")] == stockName):
                            listbox.delete(i, i)
                            break
            else:
                if (float(without_comma (currentPrice.text)) >= float(limitPrice)):
                    send_stock_update_mail(stockName, limitPrice,userMail)

                    # followSheet.update_cell(followed.row, followed.col + 4, 'YES')
                    Followers.update_one({'Username':followed['Username'], 'Stock':followed['Stock']},{'$set':sent_update})

                    for i in range(listbox.size() - 1, -1, -1):
                        stock_name_to_check = listbox.get(i, i)[0]
                        if (stock_name_to_check[0:stock_name_to_check.rfind(" --> ")] == stockName):
                            listbox.delete(i, i)
                            break


        time.sleep(60)


def add_to_stocks_list(listbox, stock_name, limit_asker, currentPrice,userName,userMail):
    """ A function used to add the searched stock to the user's list.
    
    Parameters
    ----------
    listbox: The stocks list of the user.
    stock_name: The stocks full name of the one the user search for.
	line1: A line that shows the stock name and price,changes to blank.
	limit_asker: The entry of the limit price of the user.
	currentPrice: the stock's current price.

	Add the stock and the requested price to the database
	and the user's list a, if fails popups an error window. 
    """   

    global line1
    line1.config(text="")
    already_follow_stock = 0

    # follow_list = followSheet.findall(userMail)
    # follow_list=list(Followers.find({'Mail':userMail}))

    over = '0'
    limit = str(limit_asker.get())
    try:
        float(without_comma(limit))
    except ValueError:
        create_pop_window("Error: Wrong price input", "You didn't entered your price right\n", "360x120", "Try again",
                          "", "")


    else:
        if (currentPrice > float(limit)):
            over = '1'

        update=({'Username':userName,'Mail':userMail ,'Stock':stock_name, 'Price':limit,'Over':over, 'Sent':"NO"})
# Followers.update_one({'Username':followed['Username'], 'Stock':followed['Stock']},{$'set':update})


        
        document=Followers.find_one({'Username':userName,'Stock':stock_name})            
        if(document!=None):    
            if(document['Sent'] == "NO"):
                create_pop_window("Already follow", "Already follow,this stock, now using new price limit\n", "450x100","Close", "", "")

            Followers.update_one(document,{'$set':update})



        # for followed in follow_list:
        #     if (followSheet.cell(followed.row, followed.col + 1).value == stock_name ):
                
        #         if(followSheet.cell(followed.row, followed.col + 4).value=="NO" ):
        #         	create_pop_window("Already follow", "Already follow,this stock, now using new price limit\n", "450x100","Close", "", "")
        #         already_follow_stock = 1
        #         followSheet.update_cell(followed.row, followed.col + 2, limit)
        #         followSheet.update_cell(followed.row, followed.col + 3, over)
        #         followSheet.update_cell(followed.row, followed.col + 4, 'NO')
        else:
            # followSheet.append_row([userName, userMail, stock_name, str(limit), over, 'NO'])
            Followers.insert_one(update)
            # create_pop_window("Stock added", stock_name + " added to your follow list\n", "400x100", "Close", "", "")
        for i in range(listbox.size() - 1, -1, -1):
            stock_name_to_check = listbox.get(i, i)[0]
            if (stock_name_to_check[0:stock_name_to_check.rfind(" --> ")] == stock_name):
                listbox.delete(i, i)
        listbox.insert(END, stock_name + " --> " + limit)

def ask_log_out(master,userName,userMail):
    create_pop_window("Log out?", "Are you sure you want to log out?", '400x100', "No!", "Yes",lambda: log_out(master,userName,userMail) )
    
def log_out(master,userName,userMail):
    global logged_in
    logged_in=0
    master.destroy()
    start_log_reg_window()

def sign_out(master,userName,userMail):

    global logged_in
    logged_in=0

    # stocks= followSheet.findall(userMail)
    # user=usersSheet.find(userMail)
    # usersSheet.delete_rows(user.row)

    # rows_to_delete=[]
    # for stock in stocks:
    #     # rows_to_delete.append(stock.row)
    #     followSheet.delete_rows(stock.row)

    Users.delete_one({'Username':userName})
    Followers.delete_many({'Username':userName,'Sent':"NO"})




    master.destroy()    
    start_log_reg_window()

def ask_sign_out(master,userName,userMail):

    create_pop_window("Sign out?", "Are you sure you want to sign out?", '400x100', "No!", "Yes",lambda: sign_out(master,userName,userMail) )
    

def without_comma(input):
	output = re.sub('[,]', '', input)
	return (output)

def searchClicked(master,listbox,stock_name_to_search,userName,userMail):

    """ A function used to add 2 frames to the main window,
     present the current price of the requested stock to the user
     and ask for his / her limit price to be notified.
    
    Parameters
    ----------
    master: The main window.
    listbox: The stocks list of the user.
 	stock_name_to_search: The stock's name entered by the user.
    """
    global line1
    if(isinstance(line1, str)==False):
       line1.config(text="")

    stock_name_and_price = getStockName(stock_name_to_search,1)
    stockName = stock_name_and_price[0:stock_name_and_price.rfind(' ') - 7]
    currentPrice = stock_name_and_price[stock_name_and_price.rfind(' ') + 1:len(stock_name_and_price)]
    # print(stock_name_and_price)
    # print(stockName)
    # print(currentPrice)

    if (stockName == ""):
        create_pop_window("Error: Empty stock name", "You didn't entered the stock symbol right\n", "360x120",
                          "Try again", "", "")

    else:

        stock_deatail_frame_name_and_price = Frame(master)
        stock_deatail_frame_name_and_price.grid(row=2, column=0, sticky=W)
        stock_deatail_frame_name_and_price['bg'] = screenBackground
        line1 = Label(stock_deatail_frame_name_and_price, font=labelFont, text=stock_name_and_price,
                      background=screenBackground)
        line1.grid(row=0, column=0)

        stock_deatail_frame_limit_asker = Frame(master)
        stock_deatail_frame_limit_asker.grid(row=3, column=0)
        stock_deatail_frame_limit_asker['bg'] = screenBackground

        line2 = Label(stock_deatail_frame_limit_asker, font=labelFont,
                      text='Let me now when it is under / over: (e.g. 12.34) ', background=screenBackground)
        line2.grid(row=0, column=0)


        limitAsker = Entry(stock_deatail_frame_limit_asker)
        limitAsker.grid(row=0, column=1)

        b3 = Button(stock_deatail_frame_limit_asker, font=labelFont, text='Add to my follow list', height=0,
                    background="#00ff00",
                    command=lambda: add_to_stocks_list(listbox, stockName, limitAsker, float(without_comma(currentPrice)),userName,userMail))
        b3.grid(row=0, column=2, padx=6)


##### Registration and login window


def start_log_reg_window():    
    logRegWindow = Tk()
    logRegWindow.resizable(0, 0)
    logRegWindow.title('Stocker - Wellcome')
    icon = PhotoImage(file='icon.png')
    logRegWindow.iconphoto(False, icon)
    logRegWindow.geometry('350x150')

    Label(logRegWindow, text='User Name: ', font=labelFont).grid(row=0, column=0)
    Label(logRegWindow, text='Password: ', font=labelFont).grid(row=2, column=0)

    userNameEntry = Entry(logRegWindow, width=28)
    passwordEntry = Entry(logRegWindow, show="*", width=28)

    # randomForConfirmaionMail = int((random.random()) * 1000000)
    # sendCodeButton = Button(logRegWindow, text='Send code', font=("David", 11), width=7, height=1,
    #                         command=lambda: send_confirmation_code(randomForConfirmaionMail))

    userNameEntry.grid(row=0, column=1)
    passwordEntry.grid(row=2, column=1)


    # def register(user_name_to_check,user_mail_to_check,password_to_check,repeat_password_to_check):



    # global registerButton
    registerButton = Button(logRegWindow, text='Registration', 
    	command=lambda: RegistrationSelected(logRegWindow,registerButton,userNameEntry,passwordEntry),
                            background=buttonGrayBackground)
    loginButton = Button(logRegWindow, text='Login', command=lambda: login(logRegWindow, str(userNameEntry.get()),str(passwordEntry.get())), background=buttonGrayBackground)

    registerButton.grid(row=5, column=1)
    loginButton.grid(row=6, column=1)


    logRegWindow.mainloop()

# from Window import Window

if(__name__ == "__main__"):
    start_log_reg_window()
 #    # y=Tk()
 #    # y.mainloop()

 #    x=Window("Stocker - Welcome!",{})
 #    x.startTk()
 #    # dictionary={"one" : 1, "two": 2}
 #    x.use_icon()
 #    dictionary2={"userNameLabel":Label(x, text='User Name: ', font=labelFont),
	# 	"userNameEntry" : Entry(x, width=28),
	# 	"emailLabel" : Label(x, text='EMAIL: ', font=labelFont),
	# 	"userMailEntry": Entry(x, width=28),
	# 	"passwordLabel": Label(x, text='Password: ', font=labelFont),
	# 	"passwordEntry" : Entry(x, show="*", width=28),
	# 	"repeatPasswordLabel" : Label(x, text='Reapet password: ', font=labelFont),
	# 	"reapetPasswordEntry" : Entry(x, show="*", width=28),
	# 	"confirmationCodeLabel" : Label(x, text='Confirmation code: ', font=labelFont),
	# 	"confirmationCodeEntry" : Entry(x, width=28),
	# 	"registerButton" : Button(x, text='Registration',command=lambda: RegistrationSelected(x,registerButton,userNameEntry,passwordEntry),background=buttonGrayBackground),
	# 	"loginButton" : Button(x, text='Login', command=lambda: login(x, str(userNameEntry.get()),str(passwordEntry.get())), background=buttonGrayBackground)}
	# # x.dictionary=dictionary2



	