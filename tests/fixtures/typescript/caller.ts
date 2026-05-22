/**
 * Caller module that uses BaseClass and DerivedClass.
 */

import { BaseClass, helperFunction } from './base';
import { DerivedClass } from './derived';

/**
 * Main processing function that calls methods from base and derived.
 */
export function processObjects(): void {
    const base = new BaseClass("BaseObject");
    const derived = new DerivedClass("DerivedObject", 42);

    // Call methods on base class
    const baseName = base.getName();
    const baseResult = base.calculate(10, 20);
    base.printInfo();

    // Call methods on derived class
    const derivedName = derived.getName();
    const derivedResult = derived.processData(5, 10);
    const idValue = derived.getId();

    // Call standalone helper
    const helperResult = helperFunction(baseResult);

    console.log(`Processed: ${baseName}, ${derivedName}`);
}

/**
 * Calculate total using DerivedClass.
 */
export function calculateTotal(x: number, y: number): number {
    const obj = new DerivedClass("Calculator", 1);
    return obj.processData(x, y);
}
