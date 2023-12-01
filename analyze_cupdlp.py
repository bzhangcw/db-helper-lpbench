"""typical abip schema
{
}
"""
import json
import pandas as pd

def cupdlp_string_to_result(fpath):
    with open(fpath, "r") as f:
        content = json.load(f)
        # res_primal = content['pres']
        # res_dual = content['dres']
        # sol_time = content['time']
        # sol_status = content['status']
        # val_primal = content['pobj']
        # val_dual = content['dobj']
        name = (
            fpath.split("/")[-1]
            .split(".")[0]
            .replace("s_pre", "pre")
            .replace("s_", "pre_")
            .replace("-stat", "")
        )
        return dict(
            iteration_num=content["nIter"],
            ipm_num=0,
            res_primal=content["dPrimalFeas"],
            res_dual=content["dDualFeas"],
            sol_time=content["dSolvingTime"],
            val_primal=content["dPrimalObj"],
            val_dual=content["dDualObj"],
            matvec=content.get("nAxCalls", 0),
            sol_status="opt",
            name=name,
        )
