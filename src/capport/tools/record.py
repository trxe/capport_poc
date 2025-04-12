import argparse
import datetime as dt
import json
import time
from pathlib import Path

import requests

from capport.tools.date import strftime, strptime
from capport.tools.logger import Logger


def record_endpoint_json(url: str, until: dt.datetime, prefix: str, out_dir: str, interval_s: int):
    curr = dt.datetime.now()
    Logger.log(f"Time now: {strftime(curr)}")
    Logger.log(f"Time until: {strftime(until)}")
    od = Path(out_dir)
    if not od.exists():
        od.mkdir(parents=True)
    if until < curr:
        Logger.log(f"Past starting time {strftime(until)}")
        return
    while curr <= until:
        filename = f"{prefix}_{strftime(curr)}.json"
        fp = Path(od, filename)
        try:
            resp = requests.get(url, timeout=interval_s)
            with open(fp, "+w") as file:
                json.dump(resp.json(), file)
            Logger.log(
                f"Wrote to {fp}, next run at {strftime(curr + dt.timedelta(seconds=interval_s))} in {interval_s}s"
            )
            time.sleep(interval_s)
        except requests.exceptions.Timeout as e:
            Logger.warn(
                f"Timeout connecting to {url},\nnext run at {strftime(curr + dt.timedelta(seconds=interval_s))} in {interval_s}s"
            )
        finally:
            curr = dt.datetime.now()
    Logger.log(f"Completed recording at {od}")


def main():
    ap = argparse.ArgumentParser("endpoint recorder")
    ap.add_argument("-url", help="URL to record", required=True)
    ap.add_argument("-until", help="datetime to record until", required=True)
    ap.add_argument("-prefix", help="filename prefix to record into", required=True)
    ap.add_argument("-out", help="output dir", required=True)
    ap.add_argument("-int", help="recording interval", default=10, type=int)
    args = ap.parse_args()
    record_endpoint_json(
        url=args.url,
        until=strptime(args.until),
        prefix=args.prefix,
        out_dir=args.out,
        interval_s=args.int,
    )


if __name__ == "__main__":
    main()
