# test script to summarize all results
# @author Chuwen Zhang
# @usage: python analyze.py -h
#
import json
import logging
import os
import time
import datetime
import pandas as pd

from analyze_google_pdhg import google_pdhg_string_to_result
from analyze_google_pdhg_julia import pdlp_julia_string_to_result
from analyze_abip import abip_string_to_result, abipc_string_to_result
from analyze_cupdlp import cupdlp_string_to_result

# from analyze_gurobi import gurobi_string_to_result
# from analyze_scs import scs_string_to_result
from analyze_copt import copt_string_to_result

DEFAULT_CONF = "./conf.analyze.json"
ANALYZE_METHOD_REGISTRY = {
    # "gurobi_simplex": gurobi_string_to_result,
    # "gurobi_dual": gurobi_string_to_result,
    # "gurobi_barrier": gurobi_string_to_result,
    "google_pdhg_1e-6": google_pdhg_string_to_result,
    "google_pdhg_1e-4": google_pdhg_string_to_result,
    "google_pdhg_1e-8": google_pdhg_string_to_result,
    # "scs_indirect_1e-4": scs_string_to_result,
    # "scs_indirect_1e-6": scs_string_to_result,
    # "scs_direct_1e-4": scs_string_to_result
    # "scs_direct_1e-6": scs_string_to_result,
    "abip_direct_1e-4": abip_string_to_result,
    "abip_indirect_1e-4": abip_string_to_result,
    "abip_direct_1e-6": abip_string_to_result,
    "abip_indirect_1e-6": abip_string_to_result,
    "copt_barrier": copt_string_to_result,
    ###############
    # `google_pdhg_string_to_result` is a function that takes a string as input and
    # parses it to extract relevant information about the result of the Google PDHG
    # algorithm. The function is part of a larger script that analyzes the results of
    # different optimization algorithms.
    #############
    "pdlp_julia": pdlp_julia_string_to_result,
    "pdlp": google_pdhg_string_to_result,
    "abip": abip_string_to_result,
    "abip_c_barrier": abipc_string_to_result,
    "abip_c_4": abipc_string_to_result,
    "abip_c_6": abipc_string_to_result,
    ###########################
    # precision not achievable
    ###########################
    # "scs_indirect_1e-8": scs_string_to_result,
    # "scs_direct_1e-8": scs_string_to_result,
    ###########################
    "cupdlp": cupdlp_string_to_result,
}

FORMAT = "%(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

logger = logging.getLogger("@analyze")
logger.setLevel(logging.DEBUG)


def query_real_name(name):
    return (
        name.replace("coptpres", "pre")
        .replace("pre_", "")
        .replace("s_pre", "pre")
        .replace("s_", "pre_")
        .replace("-stat", "")
    )


def query_instance_name(name):
    return name.replace(".mps", "").replace(".gz", "").replace(".mat", "")


def analyze(args=None):
    fpath = args.conf
    filters = args.filters.split(",") if args.filters is not None else None
    config = json.load(open(fpath, "r"))
    dataset = config.get("dataset", fpath.split("/")[-1].split(".")[-2])
    logger.info(f"analyze {dataset}")

    instance_path = config["directory"]
    if args.result_directory is not None:
        logger.info(f"using {args.result_directory} as the instance path")
        instance_path = args.result_directory
    dfs = []
    logger.info(f"\t\-registered methods {config['methods']}")
    for m in config["methods"]:
        name = m["name"]
        logger.info(f"try {name}\n\t{m}")
        if filters is not None and name not in filters:
            print(f"\t\-method {name} not in the filters, pass")
            continue
        affix = m["affix"]
        funcname = m.get("funcname", "")
        try:
            func = (
                ANALYZE_METHOD_REGISTRY[name]
                if name in ANALYZE_METHOD_REGISTRY
                else ANALYZE_METHOD_REGISTRY[funcname]
            )
        except KeyError:
            print(f"\t\-method {name} {funcname} not registered")
            continue

        solution_path = os.path.join(instance_path, m["solution_dir"])
        results = []
        if not os.path.exists(solution_path):
            logger.debug(f"\t\-method {name} solution path does not exist")
            continue
        logger.debug(f"\t\-analyze {name} @ {solution_path}")
        for _fp in os.listdir(solution_path):
            fp = os.path.join(solution_path, _fp)
            if not fp.endswith(affix):
                continue
            try:
                r = func(fp)
                results.append(r)
            except Exception as e:
                logging.error(f"\t\-failed to analyze {name} @ {fp}")
        if len(results) > 0:
            df = (
                pd.DataFrame.from_records(results)
                .assign(
                    method=name,
                    name=lambda df: df["name"].apply(lambda x: query_instance_name(x)),
                )
                .drop_duplicates(subset=["name", "method"])
            )
            dfs.append(df)

        logger.info(f"\t\-{name} solution finished")
    df_agg = pd.concat(dfs).fillna(0)

    instances = df_agg["name"].unique()
    method_names = [n["name"] for n in config["methods"]]
    if filters is not None:
        method_names = [n for n in method_names if n in filters]
    index = pd.MultiIndex.from_tuples(
        list((i, m) for m in method_names for i in instances.tolist()),
        names=("name", "method"),
    )
    df_agg = (
        df_agg.set_index(["name", "method"])
        .reindex(index, fill_value="-")
        .reset_index(drop=False)
        .sort_values(["name", "method"])
        .assign(real_name=lambda df: df["name"].apply(lambda x: query_real_name(x)))
    )

    df_agg = df_agg.assign(dataset=dataset, version=datetime.datetime.now())

    result_stamp = int(time.time())
    return df_agg, f"{dataset}_{result_stamp}.{args.prefix}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--conf", type=str, help="the path for configuration")
    # only output the instances with prefix
    parser.add_argument(
        "--prefix",
        type=str,
        default=None,
        help="""prefix of the examples; 
        this will output an extra output file that matches the prefix""",
    )
    parser.add_argument(
        "--filters", type=str, default=None, help="a filter for the methods to consider"
    )
    parser.add_argument(
        "--result_directory",
        type=str,
        default=None,
        help="directory you put the results, if None, will use the directory in the conf file",
    )

    args = parser.parse_args()
    df_agg, fout = analyze(args)

    # todo, how to determine if it is solved
    # is successful? todo, may have to add a ground truth
    if args.prefix is not None:
        idx_df_agg_with_prefix = df_agg["name"].apply(
            lambda x: x.startswith(args.prefix)
        )
        df_agg_pre = df_agg[idx_df_agg_with_prefix]
        bool_fail = lambda x: x.lower() in ["unfinished"]
        df_agg_pre = df_agg_pre.assign(
            bool_fail=lambda df: df.sol_status.apply(bool_fail)
        )
        df_agg_pre.to_excel(f"{fout}.xlsx", index=False)
        df_agg_pre.to_csv(f"{fout}.csv", index=False)
    else:
        df_agg.to_excel(f"{fout}.xlsx", index=False)
        df_agg.to_csv(f"{fout}.csv", index=False)
    # do some summary stats
    logger.info(f"analyze finished to with stamp {fout}")
