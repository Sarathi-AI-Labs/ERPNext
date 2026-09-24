"""Lifetime operation balances from ERPNext's authoritative Work Order rows."""

import frappe
from frappe.utils import flt


def analyze(projects, work_orders, operations, jobs, warehouses, bins, item_units):
    project_map = {p.name: p for p in projects}
    wo_map = {w.name: w for w in work_orders if w.docstatus == 1}
    balances = []
    inventory = {}
    available = {(b.item_code, b.warehouse): flt(b.actual_qty) for b in (bins or [])}
    for op in operations:
        w = wo_map.get(op.parent)
        if not w:
            continue
        p = project_map[w.project]
        planned = flt(w.qty)
        completed = (
            flt(op.get("completed_qty"))
            if op.get("completed_qty") is not None
            else None
        )
        loss = (
            flt(op.get("process_loss_qty"))
            if op.get("process_loss_qty") is not None
            else None
        )
        remaining = (
            max(planned - completed - loss, 0)
            if completed is not None and loss is not None
            else None
        )
        status = (
            (
                "Finished"
                if remaining == 0
                else (
                    "In progress"
                    if completed or op.get("actual_start_time")
                    else "Not started"
                )
            )
            if remaining is not None
            else "Unavailable"
        )
        related = [
            j
            for j in jobs
            if j.work_order == w.name
            and j.get("operation_id") == op.name
            and j.docstatus != 2
        ]
        item = op.get("finished_good") or w.production_item
        unit = item_units.get(item) if op.get("finished_good") else w.get("stock_uom")
        balances.append(
            dict(
                project=p.name,
                project_name=p.project_name,
                customer=p.customer,
                project_status=p.status,
                work_order=w.name,
                work_order_status=w.status,
                operation=op.get("operation"),
                sequence=op.get("sequence_id") or op.idx,
                workstation=op.get("workstation"),
                item=w.production_item,
                unit=w.get("stock_uom"),
                planned=planned,
                completed=completed,
                process_loss=loss,
                remaining=remaining,
                progress=(
                    min(100, completed / planned * 100)
                    if planned and completed is not None
                    else None
                ),
                status=status,
                jobs=len(related),
                corrective_jobs=sum(
                    bool(j.get("is_corrective_job_card")) for j in related
                ),
                planned_hours=flt(op.get("time_in_mins")) / 60,
                actual_hours=flt(op.get("actual_operation_time")) / 60,
                warehouse=op.get("fg_warehouse"),
                quantity_basis="Work Order output units; operation completion, not warehouse stock",
            )
        )
        if (
            w.get("track_semi_finished_goods")
            and op.get("finished_good")
            and op.get("fg_warehouse") in warehouses
        ):
            key = (item, op.fg_warehouse)
            r = inventory.setdefault(
                key,
                dict(
                    item=item,
                    warehouse=op.fg_warehouse,
                    unit=unit,
                    available=available.get(key, 0) if bins is not None else None,
                    projects=set(),
                    operations=set(),
                    basis="Shared current stock; not project allocation",
                ),
            )
            r["projects"].add(p.name)
            r["operations"].add(op.get("operation") or "")
    summaries = []
    for p in projects:
        ws = [w for w in wo_map.values() if w.project == p.name]
        ops = [r for r in balances if r["project"] == p.name]
        finished = (
            bool(ws)
            and all(w.status == "Completed" for w in ws)
            and all(r["remaining"] == 0 for r in ops)
        )
        started = any(
            flt(w.produced_qty) or w.get("actual_start_date") for w in ws
        ) or any(r["status"] in ("In progress", "Finished") for r in ops)
        summaries.append(
            dict(
                project=p.name,
                project_name=p.project_name,
                customer=p.customer,
                project_status=p.status,
                stock_tracking=(
                    "Not configured"
                    if not any(w.get("track_semi_finished_goods") for w in ws)
                    else (
                        "Configured"
                        if all(w.get("track_semi_finished_goods") for w in ws)
                        else "Partial"
                    )
                ),
                production_status=(
                    "Finished"
                    if finished
                    else "In progress" if started else "Not started"
                ),
                work_orders=len(ws),
                operations=len(ops),
                finished_operations=sum(r["status"] == "Finished" for r in ops),
                open_operations=sum(
                    r["remaining"] is not None and r["remaining"] > 0 for r in ops
                ),
                note=(
                    "No submitted Work Order"
                    if not ws
                    else (
                        "Stopped / closed work present"
                        if any(w.status in ("Stopped", "Closed") for w in ws)
                        else "Lifetime submitted production"
                    )
                ),
            )
        )
    for r in inventory.values():
        r["projects"] = ", ".join(sorted(r["projects"]))
        r["operations"] = ", ".join(sorted(r["operations"]))
    return balances, summaries, list(inventory.values())


def live_activity(projects, work_orders, jobs, logs, balances, summaries):
    """An open Job Card time log is evidence of a recorded running operation."""
    wo_map = {w.name: w for w in work_orders if w.docstatus == 1}
    log_map = {}
    for log in logs:
        log_map.setdefault(log.parent, []).append(log)
    activities = []
    for summary in summaries:
        p = next(p for p in projects if p.name == summary["project"])
        ws = [w for w in wo_map.values() if w.project == p.name]
        js = [
            j for j in jobs if j.work_order in {w.name for w in ws} and j.docstatus != 2
        ]
        times = [
            str(t)
            for j in js
            for log in log_map.get(j.name, [])
            for t in (log.get("from_time"), log.get("to_time"))
            if t
        ]
        recorded_start = bool(times)
        times += [str(j.modified) for j in js if j.get("modified")]
        running = []
        for j in js:
            w = wo_map[j.work_order]
            open_logs = [
                log
                for log in log_map.get(j.name, [])
                if log.get("from_time") and not log.get("to_time")
            ]
            if (
                not open_logs
                or j.status in ("Completed", "Cancelled", "On Hold", "On hold")
                or w.status in ("Completed", "Stopped", "Closed", "Cancelled")
            ):
                continue
            planned, completed = j.get("for_quantity"), j.get("total_completed_qty")
            running.append(
                dict(
                    project=p.name,
                    customer=p.customer,
                    job_card=j.name,
                    work_order=w.name,
                    operation=j.operation,
                    workstation=j.get("workstation"),
                    started_at=min(str(log.from_time) for log in open_logs),
                    last_activity=str(j.modified) if j.get("modified") else None,
                    planned=planned,
                    completed=completed,
                    remaining=(
                        max(
                            flt(planned)
                            - flt(completed)
                            - flt(j.get("process_loss_qty")),
                            0,
                        )
                        if planned is not None and completed is not None
                        else None
                    ),
                    unit=j.get("stock_uom"),
                    status="Running now",
                )
            )
        started = recorded_start or summary["production_status"] in (
            "In progress",
            "Finished",
        )
        paused = (
            bool(ws)
            and all(w.status in ("Stopped", "Closed", "Completed") for w in ws)
            and summary["production_status"] != "Finished"
        )
        state = (
            "Completed"
            if p.status == "Completed"
            else (
                "Cancelled"
                if p.status == "Cancelled"
                else (
                    "On hold / Stopped"
                    if p.status == "On hold" or paused
                    else (
                        "Production finished · Closure pending"
                        if summary["production_status"] == "Finished"
                        else "In progress" if started or running else "Not started"
                    )
                )
            )
        )
        # Completed, held and stopped projects cannot enter the running cards.
        if state != "In progress":
            running = []
        summary.update(
            live_status=state,
            running_operations=running,
            running_count=len(running),
            last_activity=max(times) if times else None,
            activity_message=(
                "Running now"
                if running
                else (
                    "No operation currently recorded as running"
                    if state == "In progress"
                    else state
                )
            ),
        )
        activities.extend(running)
    return activities
