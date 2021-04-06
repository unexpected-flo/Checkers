import checkers_rules as rules

bp_img = "./black_pawn.png"
bq_img = "./black_queen.png"
wp_img = "./white_pawn.png"
wq_img = "./white_queen.png"
blank = "./blank.png"

images = {"{}_pawn".format(rules.players[1]): bp_img,
          "{}_queen".format(rules.players[1]): bq_img,
          "{}_pawn".format(rules.players[0]): wp_img,
          "{}_queen".format(rules.players[0]): wq_img,
          "empty": blank}

cli_display = {"{}_pawn".format(rules.players[0]): "w",
               "{}_queen".format(rules.players[0]): "W",
               "{}_pawn".format(rules.players[1]): "b",
               "{}_queen".format(rules.players[1]): "B"}
