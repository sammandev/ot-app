from django.db import migrations


def backfill_created_by(apps, schema_editor):
    ExternalUser = apps.get_model("api", "ExternalUser")
    PurchaseRequest = apps.get_model("api", "PurchaseRequest")
    Asset = apps.get_model("api", "Asset")

    user_map = {
        worker_id.lower(): user_id
        for user_id, worker_id in ExternalUser.objects.exclude(worker_id__isnull=True)
        .exclude(worker_id="")
        .values_list("id", "worker_id")
    }

    purchase_requests_to_update = []
    purchase_requests = PurchaseRequest.objects.filter(
        created_by__isnull=True,
        owner_employee__isnull=False,
    ).select_related("owner_employee")
    for purchase_request in purchase_requests.iterator(chunk_size=500):
        employee = getattr(purchase_request, "owner_employee", None)
        worker_id = getattr(employee, "emp_id", None)
        if not worker_id:
            continue
        created_by_id = user_map.get(worker_id.lower())
        if created_by_id:
            purchase_request.created_by_id = created_by_id
            purchase_requests_to_update.append(purchase_request)

    if purchase_requests_to_update:
        PurchaseRequest.objects.bulk_update(
            purchase_requests_to_update,
            ["created_by"],
            batch_size=500,
        )

    assets_to_update = []
    assets = Asset.objects.filter(created_by__isnull=True).exclude(keeper__isnull=True).exclude(keeper="")
    for asset in assets.iterator(chunk_size=500):
        created_by_id = user_map.get(asset.keeper.lower())
        if created_by_id:
            asset.created_by_id = created_by_id
            assets_to_update.append(asset)

    if assets_to_update:
        Asset.objects.bulk_update(assets_to_update, ["created_by"], batch_size=500)


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0052_purchaserequest_asset_created_by"),
    ]

    operations = [
        migrations.RunPython(backfill_created_by, migrations.RunPython.noop),
    ]