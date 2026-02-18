enum DutyStatus {
  inSchool,
  notInSchool,
  classwork,
}

extension DutyStatusX on DutyStatus {
  String get dbValue {
    switch (this) {
      case DutyStatus.inSchool:
        return 'in_school';
      case DutyStatus.notInSchool:
        return 'not_in_school';
      case DutyStatus.classwork:
        return 'classwork';
    }
  }

  String get label {
    switch (this) {
      case DutyStatus.inSchool:
        return 'In der Schule';
      case DutyStatus.notInSchool:
        return 'Nicht in der Schule';
      case DutyStatus.classwork:
        return 'Klassenarbeits-Modus';
    }
  }

  static DutyStatus fromDbValue(String value) {
    switch (value) {
      case 'in_school':
        return DutyStatus.inSchool;
      case 'classwork':
        return DutyStatus.classwork;
      default:
        return DutyStatus.notInSchool;
    }
  }
}
