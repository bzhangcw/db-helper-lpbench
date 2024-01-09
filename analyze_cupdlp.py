"""typical abip schema
{
}
"""
import json
import pandas as pd


def cupdlp_string_to_result(fpath):
    with open(fpath, "r") as f:
        try:
            content = json.load(f)
        except:
            content = {}
            # res_primal = content['pres']
            # res_dual = content['dres']
            # sol_time = content['time']
            # sol_status = content['status']
            # val_primal = content['pobj']
            # val_dual = content['dobj']
        name = fpath.split("/")[-1].split(".")[0]
        return dict(
            iteration_num=content.get("nIter", "-"),
            ipm_num=0,
            res_primal=content.get("dPrimalFeas", "-"),
            res_dual=content.get("dDualFeas", "-"),
            sol_time=content.get("dSolvingTime", "-"),
            sol_pre=content.get("dPresolveTime", "-"),
            sol_scale=content.get("dScalingTime", "-"),
            val_primal=content.get("dPrimalObj", "-"),
            val_dual=content.get("dDualObj", "-"),
            matvec=content.get("nAxCalls", 0),
            sol_status=content.get("terminationCode", "TIMELIMIT"),
            name=name,
        )
