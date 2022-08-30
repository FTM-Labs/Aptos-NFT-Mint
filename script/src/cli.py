from pick import pick
import create_candy_machine
import update_whitelist
import update_public_mint_time
import update_presale_mint_time
if __name__ == "__main__":
    title = 'Please choose what you want to do: '
    options = [
        'Create candy machine', 
        'Update WL for existing collection',
        'Update public mint time',
        'Update presale mint time']
    option, index = pick(options, title)
    if index == 0 :
        create_candy_machine.create()
    elif index == 1:
        update_whitelist.update()
    elif index == 2:
        update_public_mint_time.update()
    else:
        update_presale_mint_time.update()