from pick import pick
import create_candy_machine
import util
if __name__ == "__main__":
    title = 'Please choose what you want to do: '
    options = [
        'Create candy machine', 
        'Update WL for existing collection',
        'Update public mint time',
        'Update presale mint time',
        'Update mint fee per mille']
    option, index = pick(options, title)
    if index == 0 :
        create_candy_machine.create()
    elif index == 1:
        util.update_whitelist()
    elif index == 2:
        util.update_public_mint_time()
    elif index  == 3:
        util.update_presale_mint_time()
    else:
        util.update_mint_fee()