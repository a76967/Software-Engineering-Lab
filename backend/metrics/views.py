import abc
import json

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from examples.models import Example, ExampleState
from label_types.models import CategoryType, LabelType, RelationType, SpanType
from labels.models import Category, Label, Relation, Span
from projects.models import Member, Project
from projects.permissions import IsProjectAdmin, IsProjectStaffAndReadOnly


class ProgressAPI(APIView):
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]

    def get(self, request, *args, **kwargs):
        examples = Example.objects.filter(project=self.kwargs["project_id"]).values("id")
        total = examples.count()
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        if project.collaborative_annotation:
            complete = ExampleState.objects.count_done(examples)
        else:
            complete = ExampleState.objects.count_done(examples, user=self.request.user)
        data = {"total": total, "remaining": total - complete, "complete": complete}
        return Response(data=data, status=status.HTTP_200_OK)


class MemberProgressAPI(APIView):
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]

    def get(self, request, *args, **kwargs):
        examples = Example.objects.filter(project=self.kwargs["project_id"]).values("id")
        members = Member.objects.filter(project=self.kwargs["project_id"])
        data = ExampleState.objects.measure_member_progress(examples, members)
        return Response(data=data, status=status.HTTP_200_OK)


class LabelDistribution(abc.ABC, APIView):
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]
    model = Label
    label_type = LabelType

    def get(self, request, *args, **kwargs):
        labels = self.label_type.objects.filter(project=self.kwargs["project_id"])
        examples = Example.objects.filter(project=self.kwargs["project_id"]).values("id")
        members = Member.objects.filter(project=self.kwargs["project_id"])
        data = self.model.objects.calc_label_distribution(examples, members, labels)
        return Response(data=data, status=status.HTTP_200_OK)


class CategoryTypeDistribution(LabelDistribution):
    model = Category
    label_type = CategoryType


class SpanTypeDistribution(LabelDistribution):
    model = Span
    label_type = SpanType


class RelationTypeDistribution(LabelDistribution):
    model = Relation
    label_type = RelationType
    
    
class SpanDisagreementSummary(APIView):
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]

    def get(self, request, *args, **kwargs):
        project_id = self.kwargs["project_id"]
        examples = Example.objects.filter(project_id=project_id).prefetch_related("spans", "assignments")
        span_types = SpanType.objects.filter(project_id=project_id).values("id", "text")
        label_map = {st["id"]: st["text"] for st in span_types}

        rows = []
        for ex in examples:
            assigned_users = list(ex.assignments.values_list("assignee_id", flat=True))
            if len(assigned_users) < 2:
                continue

            spans = list(
                Span.objects.filter(example=ex).values(
                    "user_id",
                    "label_id",
                    "start_offset",
                    "end_offset",
                )
            )
            if not spans and not ExampleState.objects.filter(example=ex).exists():
                continue

            user_spans = {uid: [] for uid in assigned_users}
            for s in spans:
                if s["user_id"] in user_spans:
                    user_spans[s["user_id"]].append(s)

            signatures = []
            for uid in assigned_users:
                lst = user_spans.get(uid, [])
                simple = [(sp["start_offset"], sp["end_offset"], sp["label_id"]) for sp in lst]
                simple.sort()
                signatures.append(json.dumps(simple))

            if len(set(signatures)) <= 1:
                continue

            signature_counts: dict[str, int] = {}
            for sig in signatures:
                signature_counts[sig] = signature_counts.get(sig, 0) + 1

            label_counts: dict[int, int] = {}
            for uid in assigned_users:
                labels_used = {sp["label_id"] for sp in user_spans.get(uid, [])}
                for lid in labels_used:
                    label_counts[lid] = label_counts.get(lid, 0) + 1

            confirmed_users = set(
                ExampleState.objects.filter(example=ex).values_list(
                    "confirmed_by_id", flat=True
                )
            )
            abstention = sum(
                1 for uid in confirmed_users if len(user_spans.get(uid, [])) == 0
            )
            x_count = sum(
                1
                for uid in assigned_users
                if uid not in confirmed_users and len(user_spans.get(uid, [])) == 0
            )

            majority = max(signature_counts.values())
            agreement = round((majority / len(signatures)) * 100)

            rows.append(
                {
                    "id": ex.id,
                    "snippet": (ex.text or "")[:100],
                    "labels": {
                        label_map.get(lid, str(lid)): cnt
                        for lid, cnt in label_counts.items()
                    },
                    "abstention": abstention,
                    "x": x_count,
                    "total": len(signatures),
                    "agreement": agreement,
                }
            )

        return Response(data=rows, status=status.HTTP_200_OK)


class DisagreementDecisionAPI(APIView):
    """Persist disagreement decisions into the example meta field."""

    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]

    def post(self, request, *args, **kwargs):
        project_id = self.kwargs["project_id"]
        decisions = request.data.get("decisions", [])
        for item in decisions:
            ex_id = item.get("id")
            decision = item.get("decision")
            try:
                ex = Example.objects.get(id=ex_id, project_id=project_id)
            except Example.DoesNotExist:
                continue

            meta = ex.meta or {}
            if decision is None:
                meta.pop("disagreement_decision", None)
            else:
                meta["disagreement_decision"] = bool(decision)
            ex.meta = meta
            ex.save(update_fields=["meta"])

        return Response({"detail": "saved"}, status=status.HTTP_200_OK)