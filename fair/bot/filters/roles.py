from telebot.custom_filters import SimpleCustomFilter


class IsOwnerFilter(SimpleCustomFilter):
    key = 'is_owner'

    def __init__(self, owner_tg_id: int):
        super().__init__()
        self.owner_tg_id = owner_tg_id

    def check(self, update):
        return update.from_user.id == self.owner_tg_id
