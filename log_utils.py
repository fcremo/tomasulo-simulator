def get_log_str(env, name, msg, *fmtargs):
    if name is None:
        return "CLK {:>5n} | {}".format(env.now, msg.format(*fmtargs))
    else:
        return "CLK {:>5n} | {} | {}".format(env.now, name, msg.format(*fmtargs))


def log_with_time(env, name, msg, *fmtargs):
    print(get_log_str(env, name, msg, *fmtargs))


def get_logger(env, name):
    def log(msg, *fmtargs):
        print(get_log_str(env, name, msg, *fmtargs))
    return log
