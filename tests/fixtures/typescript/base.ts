/**
 * Base class for testing TypeScript indexing.
 */

export class BaseClass {
    protected name: string;

    constructor(name: string) {
        this.name = name;
    }

    /**
     * Get the name of the object.
     */
    getName(): string {
        return this.name;
    }

    /**
     * Print information about the object.
     */
    printInfo(): void {
        console.log(`BaseClass: ${this.name}`);
    }

    /**
     * Calculate sum of two numbers.
     */
    calculate(x: number, y: number): number {
        return x + y;
    }
}

/**
 * Helper function that doubles a value.
 */
export function helperFunction(value: number): number {
    return value * 2;
}
