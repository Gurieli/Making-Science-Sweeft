
def check_validity(email_to_check, pass_to_check):
    if len(email_to_check) > 5 and "@" in email_to_check and len(pass_to_check) > 7 and email_to_check[0] != "@":
        return True
    else:
        return False


