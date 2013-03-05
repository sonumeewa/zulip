from optparse import make_option

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from zephyr.lib.actions import do_deactivate, user_sessions
from zephyr.models import UserProfile

class Command(BaseCommand):
    help = "Deactivate a user, including forcibly logging them out."

    option_list = BaseCommand.option_list + (
        make_option('-f', '--for-real',
                    dest='for_real',
                    action='store_true',
                    default=False,
                    help="Actually deactivate the user. Default is a dry run."),
        )

    def handle(self, *args, **options):
        if not args:
            print "Please specify an e-mail address."
            exit(1)
        user = User.objects.get(email__iexact=args[0])
        user_profile = UserProfile.objects.get(user=user)

        sessions = user_sessions(user)
        print "Deactivating %s (%s) - %s" % (user_profile.full_name, user.email,
                                             user_profile.realm.domain)
        print "%s has the following active sessions:" % (user.email,)
        for session in sessions:
            print session.expire_date, session.get_decoded()
        print ""

        if not options["for_real"]:
            print "This was a dry run. Pass -f to actually deactivate."
            exit(1)

        do_deactivate(user_profile)
        print "Sessions deleted, user deactivated."
