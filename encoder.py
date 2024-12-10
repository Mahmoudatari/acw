import hashlib

def sort(applicable_transformations):
    def sha256_key(t):
        # Use transformation_name instead of str(t)
        s = t.transformation_name.encode('utf-8')
        return hashlib.sha256(s).hexdigest()
    return sorted(applicable_transformations, key=sha256_key)

def hamming_encode(data):
    """
    Encodes a 2-bit message into 4 bits using Hamming (4,2).
    """
    # Extract the two data bits
    d1, d2 = data[0], data[1]

    # Calculate parity bits
    p1 = d1 ^ d2  # XOR of data bits
    p2 = d1       # Copy of the first data bit

    # Return encoded message: [p1, p2, d1, d2]
    return [p1, p2, d1, d2]


def Encoder(C, T, w, n,l,e):
    """
    Encodes a given code snippet with a specifc watermark 
        Parameters:
        C (str): The code snippet to be encoded.
        T (list): A list of transformations.
        w (list): The watermark to embed in the code snippet.
        n (int): The first n transformation to apply to the code snippet.
        l (int): The length of the encoded watermark.
        e (int): The number of allowed errors in the watermark.
    
    """
    T_a = [] #Initialize an empty list to store applicable transformations
    C_w = C #Initialize the transformed code to be the code snippet

    #Iterate through the list of transformations
    for t in T:
        if t.is_applicable(C):
            T_a.append(t) #Append the transformation to the list of applicable transformations
    
    #Sort the list of applicable transformations
    T_a = sort(T_a)

    print("\nSorted applicable transformations:\n")

    for i, t in enumerate(T_a, 1):
        print(f"Transformation {i}:  {t.transformation_name}\n")

    print(f"First {n} transformation(s) will be applied:\n")
    
    #Apply the first n transformations to the code snippet
    for t in T_a[:n]:
        C_w = t.transform(C_w)
    
    #Encode the watermark
    W_en = hamming_encode(w)

    print(f"\nEncoded Watermark:\n{W_en}\n")

    for i, t in enumerate(T_a[n:n+l], 0):
        if W_en[i] == 1:
            print(f"Applying transformation {i+n+1} to the code snippet based on watermark.")
            C_w = t.transform(C_w)

    return C_w

        
    
    