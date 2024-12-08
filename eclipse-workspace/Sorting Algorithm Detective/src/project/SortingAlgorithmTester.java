package project;
import java.util.Random;

//-----------------------------------------------------
//Title: Sorting Algorithm Tester
//Author: Poyraz Koca
//Description: This program tests different sorting algorithms with various types of arrays: ascending, descending, and random. It measures the execution time of each sorting algorithm and prints the results.
//-----------------------------------------------------

public class SortingAlgorithmTester {
    public static void main(String[] args) {
  
        //adjusting the sizes as needed. I implemented for
    	//1000,2000,4000,8000,1600,32000 and 64000 respectively
        int[] ascendingArray = generateAscendingArray(2000); 
        int[] descendingArray = generateDescendingArray(2000); 
       int[] randomArray = generateRandomArray(2000); 


         //Test sorting algorithms
       testSortingAlgorithm("sort1", ascendingArray);
         testSortingAlgorithm("sort1", randomArray);
       testSortingAlgorithm("sort1", descendingArray);
        System.out.println("  ");
      
     testSortingAlgorithm("sort2", ascendingArray);
       testSortingAlgorithm("sort2", randomArray); 
        testSortingAlgorithm("sort2", descendingArray);
       
       
        System.out.println("  ");
     
      testSortingAlgorithm("sort3", ascendingArray);
        testSortingAlgorithm("sort3", randomArray);
        testSortingAlgorithm("sort3", descendingArray);
        
        System.out.println("   ");
       
       testSortingAlgorithm("sort4", ascendingArray);
          testSortingAlgorithm("sort4", randomArray);
        testSortingAlgorithm("sort4", descendingArray);
        
        System.out.println(" ");
        
      testSortingAlgorithm("sort5", ascendingArray);
        
        
       testSortingAlgorithm("sort5", randomArray);
       testSortingAlgorithm("sort5", descendingArray); 
       
       
   }
    
  //--------------------------------------------------------
 // Summary: Tests a sorting algorithm specified by methodName 
 // with the given array and measures its execution time.
 // Precondition: methodName is a string specifying the name
 // of the sorting algorithm to test. array is an array of integers.
 // Postcondition: Executes the specified sorting algorithm on 
 // the array, measures time taken for execution and prints
 //--------------------------------------------------------
   
    private static void testSortingAlgorithm(String methodName, int[] array) {
        long startTime = System.currentTimeMillis();
        
        switch (methodName) {
            case "sort1":
                  SortingAlgorithms.sort1(array, 1398706147L); // Adjust student ID as needed
                break;
           case "sort2":
              SortingAlgorithms.sort2(array, 1398706147L); // Adjust student ID as needed
                break;
          case "sort3":
        	  
                SortingAlgorithms.sort3(array, 1398706147L); // Adjust student ID as needed
                break;
            case "sort4":
                SortingAlgorithms.sort4(array, 1398706147L); // Adjust student ID as needed
                break;
            case "sort5":
            	
            	
             SortingAlgorithms.sort5(array, 1398706147L); // Adjust student ID as needed
                break;
            default:
                System.out.println("Invalid sorting method name.");
                return;
        }
        long endTime = System.currentTimeMillis();
        long executionTime = endTime - startTime;
        System.out.println(methodName + " Execution Time: " + executionTime + " milliseconds");
    }
    
    
  //--------------------------------------------------------
 // Summary: Generates an array of integers arranged in descending order.
 // Precondition: size is a positive integer.
 // Postcondition: //for generating the array of inetegrs arranged in descending order
 //--------------------------------------------------------
    private static int[] generateDescendingArray(int size) {
        int[] array = new int[size];
        
        
        for   (int i = 0; i < size; i++) {
            array[i] = size - i;
        }
        return array;
    }
    
    //--------------------------------------------------------
    // Summary: Generates an array of integers arranged in ascending order.
    // Precondition: size is a positive integer.
  //for generating the array of inetegrs arranged in ascending order
    private static int[] generateAscendingArray(int size) {
        int[] array = new int[size];
        for (int i = 0; i < size; i++) {
            array[i] = i;
        } return array;
    }

    

  //--------------------------------------------------------
 // Summary: Generates an array of random integers.
 // Precondition: size is a positive integer.
 // Postcondition: Returns an array of integers of size 'size' 
 // where each element is a randomly generated integer.
 //--------------------------------------------------------
    private static int[] generateRandomArray(int size) {
        int[] array = new int[size];
        
        Random random = new Random();
        
          for (int i = 0; i < size; i++) {
            array[i] = random.nextInt();
        }
           return array; }
}
