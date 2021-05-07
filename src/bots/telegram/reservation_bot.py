#!/usr/bin/python

import logging
from enum import IntEnum
from enum import unique

from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Dispatcher
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.replykeyboardremove import ReplyKeyboardRemove
from telegram.update import Update

from bots.telegram.cron_interactions import CronInteractions
from bots.telegram.web_interactions import get_all_reservations
from bots.telegram.web_interactions import get_balance
from utils.secret_loader import load_from_secret_file

#
# Enable logging
#
logging.basicConfig(
    format="[%(levelname)s][%(asctime)s - %(name)s] %(message)s",
    level=logging.DEBUG
)

#
# Bot attributes
#
BOT_NAME = "ReservationBot"
BOT_VERSION = "0.0.1"

LOGGER = logging.getLogger(__name__)
MIN_ALERT = 1
MAX_ALERT = 40

IS_ACTIVATED = False
CRON_INTERACTIONS = CronInteractions()
CREATION_CRON_INFO = None
BALANCE_ALERT = None

#
# STRING CONSTANTS
#
INACTIVE_MSG = "Bot is inactive. Please activate it using the /start command"


#
# Bot commands
#
@unique
class CmdStatus(IntEnum):
    HELP = 1
    VERSION = 2
    START = 3
    STOP = 4
    RESET = 5
    SHOW_RESERVATION_CRONS = 6
    SHOW_RESERVATIONS = 7
    SHOW_BALANCE = 8
    SETUP_RESERVATION_CRON = 9
    SETUP_RESERVATION_CRON_START_TIME = 10
    SETUP_RESERVATION_CRON_GAME_TIME = 11
    REMOVE_RESERVATION_CRON = 12
    SETUP_BALANCE_ALERT = 13
    REMOVE_BALANCE_ALERT = 14


def show_help(update: Update, _: CallbackContext) -> int:
    LOGGER.debug("Received new request: help")

    update.message.reply_text(
        "/help : Displays this help message\n"
        + "/version : Displays the ReservationBot version\n"
        + "/start : Activates the ReservationBot\n"
        + "/stop : Deactivates the ReservationBot\n"
        + "/reset : Resets all the stored data and cron jobs\n"
        + "/show_reservation_crons : Shows the active reservation cron jobs\n"
        + "/show_reservations : Lists the reservations\n"
        + "/show_balance : Shows the account balance\n"
        + "/setup_reservation_cron : Helper to setup a new reservation cron job\n"
        + "/remove_reservation_cron : Helper to remove a reservation cron job\n"
        + "/setup_balance_alert : Helper to setup an account balance alert\n"
        + "/remove_balance_alert : Helper to remove the account balance alert\n"
    )
    return CmdStatus.HELP.value


def version(update: Update, _: CallbackContext) -> int:
    global BOT_NAME
    global BOT_VERSION

    LOGGER.debug("Received new request: version")

    update.message.reply_text(
        str(BOT_NAME) + " version " + str(BOT_VERSION)
    )
    return CmdStatus.VERSION.value


def start(update: Update, _: CallbackContext) -> int:
    global BOT_NAME
    global BOT_VERSION
    global IS_ACTIVATED

    LOGGER.info("Bot started: Name = %s, Version = %s", str(BOT_NAME), str(BOT_VERSION))

    IS_ACTIVATED = True

    update.message.reply_text(
        "Hi! My name is "
        + str(BOT_NAME)
        + ". I will handle the paddle tennis reservations for you.\n"
        + "Type /help to check the available commands"
    )
    return CmdStatus.START.value


def stop(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED

    LOGGER.info("Bot stopped")

    IS_ACTIVATED = False

    update.message.reply_text(
        "I am now inactive. Cron jobs will still be executed though.\n"
        + "Type /start to enable me again"
    )
    return CmdStatus.STOP.value


def reset(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global CRON_INTERACTIONS

    LOGGER.info("Bot reset")

    prev_is_activated = IS_ACTIVATED
    IS_ACTIVATED = False

    LOGGER.debug("Erasing all crons...")
    CRON_INTERACTIONS.clear()

    IS_ACTIVATED = prev_is_activated

    update.message.reply_text(
        "All my data has been reset!"
    )
    return CmdStatus.RESET.value


def show_reservation_crons(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global CRON_INTERACTIONS

    LOGGER.debug("Received new request: show_reservation_crons")

    if IS_ACTIVATED:
        update.message.reply_text(
            "Active cron jobs:\n"
            + " ID | GAME DAY | GAME START TIME | GAME DURATION \n"
            + "\n".join(
                [" " + str(cron_id) + "       " + str(game_day) + "                  " + str(
                    game_start_time) + "                  " + str(
                    game_duration) for cron_id, (game_day, game_start_time, game_duration) in
                 enumerate(CRON_INTERACTIONS.get_active_crons())],
            ),
        )
    else:
        update.message.reply_text(INACTIVE_MSG)

    return CmdStatus.SHOW_RESERVATION_CRONS.value


def show_reservations(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED

    LOGGER.debug("Received new request: show_reservations")

    if IS_ACTIVATED:
        reservations = get_all_reservations()

        update.message.reply_text(
            "Reservations:\n"
            + " GAME DAY | GAME START TIME | GAME END TIME | LOCATION \n"
            + "\n".join(
                [str(game_day) + " " + str(game_start_time) + " " + str(game_end_time) + " " + str(game_field) for
                 game_day, game_start_time, game_end_time, game_field in reservations])
        )
    else:
        update.message.reply_text(INACTIVE_MSG)

    return CmdStatus.SHOW_RESERVATIONS.value


def show_balance(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED

    LOGGER.debug("Received new request: show_balance")

    if IS_ACTIVATED:
        balance = get_balance()

        update.message.reply_text(
            "Current Balance: " + str(balance)
        )
    else:
        update.message.reply_text(INACTIVE_MSG)

    return CmdStatus.SHOW_BALANCE.value


def show_balance_alert(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global BALANCE_ALERT

    LOGGER.debug("Received new request: show_balance_alert")

    if IS_ACTIVATED:
        if BALANCE_ALERT:
            update.message.reply_text(
                "Current Balance Alert set to : " + str(BALANCE_ALERT) + " euros"
            )
        else:
            update.message.reply_text("Balance Alert is not set")
    else:
        update.message.reply_text(INACTIVE_MSG)

    return CmdStatus.SHOW_BALANCE.value


def setup_reservation_cron(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global CREATION_CRON_INFO

    LOGGER.debug("Received new request: setup_reservation_cron")

    if IS_ACTIVATED:
        CREATION_CRON_INFO = dict()
        reply_keyboard = [["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]
        update.message.reply_text(
            "Alright! Lets setup a reservation.\n"
            + "When do you want to play?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
    else:
        update.message.reply_text(INACTIVE_MSG)

    return CmdStatus.SETUP_RESERVATION_CRON.value


def setup_reservation_cron_start_time(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global CREATION_CRON_INFO

    LOGGER.debug("Received new request: setup_reservation_cron_start_time")

    if IS_ACTIVATED:
        if CREATION_CRON_INFO is None:
            update.message.reply_text("Error: Please set up the game day first or restart the whole process")
        else:
            CREATION_CRON_INFO["day"] = update.message.text

            reply_keyboard = [["9h", "10h", "11h", "12h", "13h", "14h", "15h", "16h", "17h", "18h", "19h", "20h"]]
            update.message.reply_text(
                "When should the game start?",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            )
    else:
        update.message.reply_text(INACTIVE_MSG)

    return CmdStatus.SETUP_RESERVATION_CRON_START_TIME.value


def setup_reservation_cron_game_time(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global CREATION_CRON_INFO

    LOGGER.debug("Received new request: setup_reservation_cron_game_time")

    if IS_ACTIVATED:
        if CREATION_CRON_INFO is None:
            update.message.reply_text("Error: Please set up the game day and time first or restart the whole process")
        else:
            CREATION_CRON_INFO["start_time"] = update.message.text

            reply_keyboard = [["1h", "1h30m", "2h"]]
            update.message.reply_text(
                "How many time do you want to play?",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            )
    else:
        update.message.reply_text(INACTIVE_MSG)

    return CmdStatus.SETUP_RESERVATION_CRON_GAME_TIME.value


def setup_reservation_cron_complete(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global CREATION_CRON_INFO
    global CRON_INTERACTIONS

    LOGGER.debug("Received new request: setup_reservation_cron_complete")

    if IS_ACTIVATED:
        if CREATION_CRON_INFO is None:
            update.message.reply_text(
                "Error: Please set up the game day, time, and duration first or restart the whole process"
            )
        else:
            CREATION_CRON_INFO["duration"] = update.message.text

            game_day = CREATION_CRON_INFO["day"]
            game_start_time = CREATION_CRON_INFO["start_time"]
            game_duration = CREATION_CRON_INFO["duration"]
            try:
                CRON_INTERACTIONS.cron_create(
                    game_day=game_day,
                    game_start_time=game_start_time,
                    game_duration=game_duration
                )
            except Exception:
                update.message.reply_text("Error: Internal exception creating job")
            else:
                CREATION_CRON_INFO = None
                update.message.reply_text(
                    "Your reservation cron has been created!\n"
                    + "Every " + game_day
                    + " at " + game_start_time
                    + " for " + game_duration,
                    reply_markup=ReplyKeyboardRemove()
                )
    else:
        update.message.reply_text(INACTIVE_MSG)

    return ConversationHandler.END


def setup_reservation_cron_cancel(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global CREATION_CRON_INFO

    LOGGER.debug("Cancelled setup_reservation_cron")

    if IS_ACTIVATED:
        CREATION_CRON_INFO = None
        update.message.reply_text(
            "We have cancelled your new reservation. Nothing was updated.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        update.message.reply_text(INACTIVE_MSG)

    return ConversationHandler.END


def remove_reservation_cron(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global CRON_INTERACTIONS

    LOGGER.debug("Received new request: remove_reservation_cron")

    if IS_ACTIVATED:
        reply_keyboard = [[str(i) for i in range(CRON_INTERACTIONS.get_num_active_crons())]]
        update.message.reply_text(
            "Select the id you want to remove:\n"
            + " ID | GAME DAY | GAME START TIME | GAME DURATION \n"
            + "\n".join(
                [" " + str(cron_id) + "       " + str(game_day) + "                  " + str(
                    game_start_time) + "                  " + str(
                    game_duration) for cron_id, (game_day, game_start_time, game_duration) in
                 enumerate(CRON_INTERACTIONS.get_active_crons())],
            ),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
    else:
        update.message.reply_text(INACTIVE_MSG)

    return CmdStatus.REMOVE_RESERVATION_CRON.value


def remove_reservation_cron_complete(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global CRON_INTERACTIONS

    LOGGER.debug("Received new request: remove_reservation_cron_complete")

    if IS_ACTIVATED:
        try:
            cron_id = update.message.text
            cron_id = int(cron_id)
        except Exception:
            cron_id = None
        if cron_id is None or not (0 <= cron_id < CRON_INTERACTIONS.get_num_active_crons()):
            update.message.reply_text(
                "Error: Invalid cron id. Value must be between 0 and "
                + str(CRON_INTERACTIONS.get_num_active_crons())
            )
        else:
            try:
                CRON_INTERACTIONS.cron_delete(cron_id)
            except Exception:
                update.message.reply_text(
                    "ERROR: Internal error creating cron with id " + str(cron_id),
                    reply_markup=ReplyKeyboardRemove()
                )
            else:
                update.message.reply_text(
                    "Cron with id " + str(cron_id) + " has been erased",
                    reply_markup=ReplyKeyboardRemove()
                )
    else:
        update.message.reply_text(INACTIVE_MSG)

    return ConversationHandler.END


def remove_reservation_cron_cancel(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global CREATION_CRON_INFO

    LOGGER.debug("Cancelled remove_reservation_cron")

    if IS_ACTIVATED:
        CREATION_CRON_INFO = None
        update.message.reply_text(
            "Removing reservation cron process aborted. Nothing was updated.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        update.message.reply_text(INACTIVE_MSG)

    return ConversationHandler.END


def setup_balance_alert(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED

    LOGGER.debug("Received new request: setup_balance_alert")

    if IS_ACTIVATED:
        update.message.reply_text(
            "Please provide the minimum amount at which we should alert you.\n"
            + "(just an integer number between "
            + str(MIN_ALERT)
            + " and "
            + str(MAX_ALERT)
            + ")"
        )
    else:
        update.message.reply_text(INACTIVE_MSG)

    return CmdStatus.SETUP_BALANCE_ALERT.value


def setup_balance_alert_complete(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global BALANCE_ALERT

    LOGGER.debug("Received new request: setup_balance_alert_complete")

    if IS_ACTIVATED:
        try:
            new_value = update.message.text
            new_value = int(new_value)
        except Exception:
            new_value = None
        if new_value is None or not (MIN_ALERT <= new_value <= MAX_ALERT):
            update.message.reply_text(
                "Error: Balance alert value should be an integer between "
                + str(MIN_ALERT)
                + " and "
                + str(MAX_ALERT)
            )
        else:
            BALANCE_ALERT = new_value
            update.message.reply_text("Balance alerting has been set to " + str(BALANCE_ALERT))
    else:
        update.message.reply_text(INACTIVE_MSG)

    return ConversationHandler.END


def setup_balance_alert_cancel(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global CREATION_CRON_INFO

    LOGGER.debug("Cancelled setup_balance_alert")

    if IS_ACTIVATED:
        update.message.reply_text(
            "Setting up balance alert process aborted. Nothing was updated.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        update.message.reply_text(INACTIVE_MSG)

    return ConversationHandler.END


def remove_balance_alert(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global BALANCE_ALERT

    LOGGER.debug("Received new request: setup_balance_alert")

    if IS_ACTIVATED:
        global BALANCE_ALERT
        BALANCE_ALERT = None
        update.message.reply_text("Balance alerting has been deactivated")
    else:
        update.message.reply_text(INACTIVE_MSG)

    return CmdStatus.REMOVE_BALANCE_ALERT.value


def reservation_done(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED
    global BALANCE_ALERT

    LOGGER.debug("Received new request: reservation_done")

    balance = get_balance()
    if BALANCE_ALERT is not None and balance < float(BALANCE_ALERT):
        update.message.reply_text(
            "!!!!ALERT!!!! Your remaining balance is under the limits\n"
            "A new reservation has been done.\n"
            + "- Current balance: " + str(balance) + "\n"
            + "Type /show_reservations to see the full list of reservations.\n"
        )
    else:
        update.message.reply_text(
            "A new reservation has been done.\n"
            + "- Current balance: " + str(balance) + "\n"
            + "Type /show_reservations to see the full list of reservations.\n"
        )

    return CmdStatus.RESERVATION_DONE.value


def reservation_failed(update: Update, _: CallbackContext) -> int:
    global IS_ACTIVATED

    LOGGER.debug("Received new request: reservation_failed")

    update.message.reply_text(
        "!!!!ALERT!!!! One of your reservation cron jobs failed\n"
        + "This is probably due to insufficient funds or because all fields are occupied"
    )

    return CmdStatus.RESERVATION_DONE.value


def unknown(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command."
    )


#
# Internal helpers
#
def _add_handlers(dispatcher: Dispatcher) -> None:
    help_handler = CommandHandler("help", show_help)
    dispatcher.add_handler(help_handler)
    version_handler = CommandHandler("version", version)
    dispatcher.add_handler(version_handler)
    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)
    stop_handler = CommandHandler("stop", stop)
    dispatcher.add_handler(stop_handler)
    reset_handler = CommandHandler("reset", reset)
    dispatcher.add_handler(reset_handler)

    show_reservation_crons_handler = CommandHandler("show_reservation_crons", show_reservation_crons)
    dispatcher.add_handler(show_reservation_crons_handler)
    show_reservations_handler = CommandHandler("show_reservations", show_reservations)
    dispatcher.add_handler(show_reservations_handler)
    show_balance_handler = CommandHandler("show_balance", show_balance)
    dispatcher.add_handler(show_balance_handler)
    show_balance_alert_handler = CommandHandler("show_balance_alert", show_balance_alert)
    dispatcher.add_handler(show_balance_alert_handler)

    setup_reservation_cron_handler = ConversationHandler(
        entry_points=[CommandHandler("setup_reservation_cron", setup_reservation_cron)],
        states={
            CmdStatus.SETUP_RESERVATION_CRON.value: [
                MessageHandler(Filters.text & ~Filters.command, setup_reservation_cron_start_time)],
            CmdStatus.SETUP_RESERVATION_CRON_START_TIME.value: [
                MessageHandler(Filters.text & ~Filters.command, setup_reservation_cron_game_time)],
            CmdStatus.SETUP_RESERVATION_CRON_GAME_TIME.value: [
                MessageHandler(Filters.text & ~Filters.command, setup_reservation_cron_complete)],
        },
        fallbacks=[CommandHandler("cancel", setup_reservation_cron_cancel)],
    )
    dispatcher.add_handler(setup_reservation_cron_handler)

    remove_reservation_cron_handler = ConversationHandler(
        entry_points=[CommandHandler("remove_reservation_cron", remove_reservation_cron)],
        states={
            CmdStatus.REMOVE_RESERVATION_CRON.value: [
                MessageHandler(Filters.text & ~Filters.command, remove_reservation_cron_complete)],
        },
        fallbacks=[CommandHandler("cancel", remove_reservation_cron_cancel)],
    )
    dispatcher.add_handler(remove_reservation_cron_handler)

    setup_balance_alert_handler = ConversationHandler(
        entry_points=[CommandHandler("setup_balance_alert", setup_balance_alert)],
        states={
            CmdStatus.SETUP_BALANCE_ALERT.value: [
                MessageHandler(Filters.text & ~Filters.command, setup_balance_alert_complete)],
        },
        fallbacks=[CommandHandler("cancel", setup_balance_alert_cancel)],
    )
    dispatcher.add_handler(setup_balance_alert_handler)

    remove_balance_alert_handler = CommandHandler("remove_balance_alert", remove_balance_alert)
    dispatcher.add_handler(remove_balance_alert_handler)


def _add_handlers_for_cron_commands(dispatcher: Dispatcher) -> None:
    reservation_done_handler = CommandHandler("reservation_done", reservation_done)
    dispatcher.add_handler(reservation_done_handler)
    reservation_failed_handler = CommandHandler("reservation_failed", reservation_failed)
    dispatcher.add_handler(reservation_failed_handler)


def _add_unknown_command_handler(dispatcher: Dispatcher) -> None:
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)


#
# MAIN
#
def main() -> None:
    token = load_from_secret_file("telegram_bot_token.txt")
    updater = Updater(token)

    # Add commands handlers
    _add_handlers(updater.dispatcher)

    # Add cron commands handlers
    _add_handlers_for_cron_commands(updater.dispatcher)

    # Add unknown command handler
    _add_unknown_command_handler(updater.dispatcher)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


#
# ENTRY POINT
#
if __name__ == "__main__":
    main()
