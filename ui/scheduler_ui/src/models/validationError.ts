import type { ValidationErrorLocItem } from './validationErrorLocItem';

export interface ValidationError {
  loc: ValidationErrorLocItem[];
  msg: string;
  type: string;
}
