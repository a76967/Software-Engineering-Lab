export class RuleVote {
    constructor(
      public id: number,
      public grid: number,
      public ruleIndex: number,
      public value: string,
      public user: string,
      public createdAt: string
    ) {}
  }