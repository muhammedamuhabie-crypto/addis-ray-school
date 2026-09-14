from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from accounts.models import User

from students.models import Student
from academics.models import Subject, ClassRoom, GradeRecord


class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Student
        fields = [
            'id',
            'student_id',
            'first_name',
            'father_name',
            'grandfather_name',
            'gender',
            'date_of_birth',
            'phone',
            'address',
            'guardian_name',
            'guardian_phone',
            'grade',
            'section',
            'stream',
            'academic_year',
            'photo',
            'username',
            'email',
            'password',
        ]

    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('father_name', ''),
            role='STUDENT'
        )

        student = Student.objects.create(
            user=user,
            **validated_data
        )

        return student


class CurrentUserSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()


class AuthorizationResponseSerializer(serializers.Serializer):

    authorized = serializers.BooleanField()
    role = serializers.CharField()
    message = serializers.CharField()


class ServiceAuthorizationSerializer(serializers.Serializer):

    authorized = serializers.BooleanField()
    role = serializers.CharField()
    service = serializers.CharField()
    message = serializers.CharField()


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = [
            'id',
            'name',
            'code',
        ]


class ClassRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassRoom
        fields = [
            'id',
            'grade',
            'section',
            'academic_year',
        ]


class GradeRecordSerializer(serializers.ModelSerializer):

    student_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()

    class Meta:
        model = GradeRecord
        fields = [
            'id',
            'student',
            'student_name',
            'subject',
            'subject_name',
            'academic_year',
            'semester',
            'mark',
        ]

    @extend_schema_field(serializers.CharField())
    def get_student_name(self, obj):
        return (
            f'{obj.student.first_name} '
            f'{obj.student.father_name}'
        )

    @extend_schema_field(serializers.CharField())
    def get_subject_name(self, obj):
        return obj.subject.name

    def validate_mark(self, value):

        if value < 0 or value > 100:
            raise serializers.ValidationError(
                'Mark must be between 0 and 100.'
            )

        return value

    def validate(self, attrs):

        student = attrs.get(
            'student',
            getattr(self.instance, 'student', None)
        )

        subject = attrs.get(
            'subject',
            getattr(self.instance, 'subject', None)
        )

        academic_year = attrs.get(
            'academic_year',
            getattr(self.instance, 'academic_year', None)
        )

        semester = attrs.get(
            'semester',
            getattr(
                self.instance,
                'semester',
                'SEMESTER_1'
            )
        )

        if student and academic_year:

            if student.academic_year != academic_year:
                raise serializers.ValidationError({
                    'academic_year':
                    'Academic year does not match the student.'
                })

        if student and subject and academic_year and semester:

            existing = GradeRecord.objects.filter(
                student=student,
                subject=subject,
                academic_year=academic_year,
                semester=semester,
            )

            if self.instance:
                existing = existing.exclude(
                    pk=self.instance.pk
                )

            if existing.exists():
                raise serializers.ValidationError(
                    'A grade record already exists for this '
                    'student, subject, academic year and semester.'
                )

        return attrs

from teachers.models import TeacherProfile


class TeacherSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    email = serializers.EmailField(
        source='user.email',
        read_only=True
    )

    role = serializers.CharField(
        source='user.role',
        read_only=True
    )

    class Meta:
        model = TeacherProfile

        fields = [
            'id',
            'username',
            'email',
            'role',
            'teacher_id',
            'first_name',
            'father_name',
            'grandfather_name',
            'gender',
            'date_of_birth',
            'phone',
            'address',
            'qualification',
            'subject',
            'grade',
            'section',
            'hire_date',
            'photo',
            'can_register_students',
            'can_take_attendance',
            'can_enter_grades',
            'can_view_reports',
        ]


class TeacherCreateSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    teacher_id = serializers.CharField(max_length=30)
    first_name = serializers.CharField(max_length=80)
    father_name = serializers.CharField(max_length=80)
    grandfather_name = serializers.CharField(max_length=80)
    gender = serializers.ChoiceField(choices=TeacherProfile.GENDERS)
    date_of_birth = serializers.DateField()
    phone = serializers.CharField(max_length=30)
    address = serializers.CharField()
    qualification = serializers.CharField(max_length=150)
    subject = serializers.CharField(max_length=120)
    grade = serializers.ChoiceField(choices=TeacherProfile.GRADES)
    section = serializers.ChoiceField(choices=TeacherProfile.SECTIONS)
    hire_date = serializers.DateField()

    can_register_students = serializers.BooleanField(default=False)
    can_take_attendance = serializers.BooleanField(default=False)
    can_enter_grades = serializers.BooleanField(default=False)
    can_view_reports = serializers.BooleanField(default=False)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'A user with this username already exists.'
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'A user with this email already exists.'
            )
        return value

    def validate_teacher_id(self, value):
        if TeacherProfile.objects.filter(teacher_id=value).exists():
            raise serializers.ValidationError(
                'A teacher with this teacher ID already exists.'
            )
        return value

    def create(self, validated_data):

        password = validated_data.pop('password')
        username = validated_data.pop('username')
        email = validated_data.pop('email')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='TEACHER'
        )

        teacher = TeacherProfile.objects.create(
            user=user,
            **validated_data
        )

        return teacher

    def to_representation(self, instance):
        return TeacherSerializer(instance).data


from attendance.models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):

    student_name = serializers.SerializerMethodField()

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Attendance
        fields = [
            'id',
            'student',
            'student_name',
            'date',
            'status',
            'status_display',
        ]

    @extend_schema_field(serializers.CharField())
    def get_student_name(self, obj):
        return (
            f'{obj.student.first_name} '
            f'{obj.student.father_name}'
        )


class StudentResultItemSerializer(serializers.Serializer):
    subject_id = serializers.IntegerField()
    subject_name = serializers.CharField()
    mark = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    final_mark = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)


class StudentResultsSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_number = serializers.CharField()
    student_name = serializers.CharField()
    grade = serializers.IntegerField()
    section = serializers.CharField()
    stream = serializers.CharField()
    academic_year = serializers.CharField()
    results = StudentResultItemSerializer(many=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    average = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    passed = serializers.BooleanField()


class StudentAverageSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_number = serializers.CharField()
    student_name = serializers.CharField()
    average = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)


class RankingItemSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_number = serializers.CharField()
    student_name = serializers.CharField()
    grade = serializers.IntegerField()
    section = serializers.CharField()
    stream = serializers.CharField()
    average = serializers.DecimalField(max_digits=6, decimal_places=2)
    rank = serializers.IntegerField()


class RankingSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    rankings = RankingItemSerializer(many=True)

# Documentation serializers for final API report endpoints

class PromotionItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    student_number = serializers.CharField()
    student_name = serializers.CharField()
    from_grade = serializers.IntegerField()
    to_grade = serializers.IntegerField(allow_null=True)
    academic_year = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()


class PromotionListSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    promotions = PromotionItemSerializer(many=True)


class PromotionCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    student_number = serializers.CharField()
    student_name = serializers.CharField()
    from_grade = serializers.IntegerField()
    to_grade = serializers.IntegerField(allow_null=True)
    academic_year = serializers.CharField()
    status = serializers.CharField()


class StudentReportRecordSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    subject_id = serializers.IntegerField()
    subject = serializers.CharField()
    semester = serializers.CharField()
    mark = serializers.DecimalField(
        max_digits=6,
        decimal_places=2
    )
    academic_year = serializers.CharField()


class StudentReportSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_number = serializers.CharField()
    student_name = serializers.CharField()
    grade = serializers.IntegerField()
    section = serializers.CharField()
    stream = serializers.CharField(allow_null=True)
    academic_year = serializers.CharField()
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    average = serializers.DecimalField(
        max_digits=6,
        decimal_places=2
    )
    passed = serializers.BooleanField()
    records = StudentReportRecordSerializer(many=True)


class ClassReportStudentSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_number = serializers.CharField()
    student_name = serializers.CharField()
    grade = serializers.IntegerField()
    section = serializers.CharField()
    stream = serializers.CharField(allow_null=True)
    average = serializers.DecimalField(
        max_digits=6,
        decimal_places=2
    )
    passed = serializers.BooleanField()
    rank = serializers.IntegerField()


class ClassReportSerializer(serializers.Serializer):
    grade = serializers.IntegerField()
    section = serializers.CharField()
    total_students = serializers.IntegerField()
    passed_students = serializers.IntegerField()
    failed_students = serializers.IntegerField()
    pass_percentage = serializers.FloatField()
    fail_percentage = serializers.FloatField()
    students = ClassReportStudentSerializer(many=True)


class SchoolPerformanceSerializer(serializers.Serializer):
    students = serializers.IntegerField()
    teachers = serializers.IntegerField()
    passed = serializers.IntegerField()
    failed = serializers.IntegerField()
    attendance_records = serializers.IntegerField()


class AttendanceReportSerializer(serializers.Serializer):
    total_records = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()

