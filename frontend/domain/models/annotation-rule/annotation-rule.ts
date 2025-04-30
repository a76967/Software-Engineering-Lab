export class AnnotationRuleGrid {
  constructor(
    public id: number,
    public project: number,
    public version: number,
    public rules: string[],
    public createdBy: string,
    public lastEditedBy: string,
    public createdAt: string,
    public updatedAt: string
  ) {}
}