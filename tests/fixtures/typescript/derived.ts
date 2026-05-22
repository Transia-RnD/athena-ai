/**
 * Derived class inheriting from BaseClass.
 */

import { BaseClass } from './base';

export class DerivedClass extends BaseClass {
    private id: number;

    constructor(name: string, id: number) {
        super(name);
        this.id = id;
    }

    /**
     * Override getName to include ID.
     */
    getName(): string {
        return `${this.name} (ID: ${this.id})`;
    }

    /**
     * Get the ID of the object.
     */
    getId(): number {
        return this.id;
    }

    /**
     * Process data using parent's calculate method.
     */
    processData(a: number, b: number): number {
        const result = this.calculate(a, b);
        return result * this.id;
    }
}
