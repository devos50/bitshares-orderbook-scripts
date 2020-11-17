from grapheneapi.grapheneapi import GrapheneAPI

rpc = GrapheneAPI("127.0.0.1", 8090)

with open("asset_precisions.txt", "w") as out_file:
    with open("missing_assets.txt", "r") as missing_assets_file:
        for line in missing_assets_file.readlines():
            missing_asset_id = line.strip()
            asset_info = rpc.get_assets([missing_asset_id])
            out_file.write("%s,%d\n" % (missing_asset_id, asset_info[0]["precision"]))
