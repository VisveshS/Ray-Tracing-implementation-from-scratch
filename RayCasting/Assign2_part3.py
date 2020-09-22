import matplotlib.pyplot as plt
import numpy as np
SIZEX=90
SIZEY=60
class face():
	def __init__(self,n,name):
		self.vertex = np.zeros((n,3))
		self.name = name
		self.normal = np.array([0,0,0])
sphereCenter=np.array([0.5,0.8+1e-3,1])
sphereRadius=0.8
right_wall = face(4,'right_wall')
left_wall = face(4,'left_wall')
back_wall = face(4,'back_wall')
ceiling = face(4,'ceiling')
floor = face(4,'floor')
cube = [face(4,'cubeTop'),face(4,'cubeFront'),face(4,'cubeSide')]
pyramid = [face(3,'pyramidLeft'),face(3,'pyramidRight'),face(3,'pyramidBack'),face(3,'pyramidBase')]
def norm(vector):
	return np.array(vector)/np.linalg.norm(vector)
def inside(polygon,point):
	cross1=np.cross(polygon[-1]-point,polygon[0]-point)
	for i in range(len(polygon)-1):
		if np.dot(cross1,np.cross(polygon[i]-point,polygon[i+1]-point))<0:
			return False
	return True;
def refract(normal,incoming,refractive_index):
	sin1=np.linalg.norm(np.cross(incoming,normal))
	sin2=sin1/refractive_index
	if sin2>1:
		return [True,incoming-2*np.dot(incoming,normal)*normal]
	theta2=np.arcsin(sin2)
	if theta2>89:theta2=89#tan90 shouln't occur
	perp=norm(incoming-normal*np.dot(normal,incoming))
	direction=1 if np.dot(normal,incoming)>0 else -1
	return [False,norm(np.tan(theta2)*perp+direction*normal)]
def collide(Face,rayDirection, rayPoint):
	ndotu = np.dot(Face.normal,rayDirection)
	if abs(ndotu) < 1e-6:
		return [False,None]
	temp = rayPoint - Face.vertex[0]
	distance = -np.dot(Face.normal,temp) / ndotu
	contanct_point = temp + distance * rayDirection + Face.vertex[0]
	if distance<0:return [False,None]
	return [True,contanct_point] if inside(Face.vertex,contanct_point) else [False,None]
def sphereCollide(rayDirection, rayPoint, fromSurface):
	D=sphereCenter-rayPoint
	if np.dot(D,rayDirection) <=0:
		return [False,None]
	if np.linalg.norm(np.cross(D,rayDirection))>=sphereRadius:
		return [False,None]
	l=np.dot(D,rayDirection)
	l=np.linalg.norm(l)
	D=np.linalg.norm(D)
	d=l-(sphereRadius**2-D**2+l**2)**.5
	return [True,rayPoint+d*rayDirection]
def rayIntersect(rayDirection, rayPoint, fromSurface):
	hit, intersection = sphereCollide(rayDirection, rayPoint,fromSurface)
	if hit and fromSurface!='sphere':
		return ['sphere',intersection]
	for Face in [pyramid[1],pyramid[0],pyramid[2],pyramid[3],cube[0],cube[1],cube[2],right_wall,left_wall,back_wall,ceiling,floor]:
		hit, intersection = collide(Face,rayDirection,rayPoint)
		if hit and Face.name!=fromSurface:
			return [Face.name,intersection]
	return [None,None]
def raycast(rayDirection, rayPoint,fromSurface,refractive_index):
	lightPosition=np.array([0,3.5,0])
	lightPositionball=np.array([0,3.5,1.5])
	lightPositionPyr=np.array([-0.5,3.5,1])
	lightPositionShadow=np.array([0,6.5,-1])
	cubelightPosition=np.array([0,2,0])
	cubeColor=np.array([0,1,0])
	sphereColor=np.array([1,0,0])
	pyramidColor=np.array([1,1,0.1])
	refractive_index_prism=1.25
	refractive_index_sphere=10
	Face, point=rayIntersect(rayDirection,rayPoint,fromSurface)
	if None:x=0
	elif Face=='sphere':
		normal=norm(point-sphereCenter)
		TIR,refractedRay=refract(normal,rayDirection,refractive_index_sphere)
		other=2*np.dot(-point+sphereCenter,refractedRay)*refractedRay+point
		normal=norm(other-sphereCenter)
		TIR,refractedRay=refract(normal,refractedRay,1/refractive_index_sphere)
		if TIR:
			return np.array([1,1,1])
		return raycast(refractedRay,other,'sphere',1)
	elif Face=='pyramidRight':
		TIR,refractedRay=refract(pyramid[1].normal,rayDirection,(1/refractive_index_prism if refractive_index!=1 else refractive_index_prism))
		refractionColor=raycast(refractedRay,point,'pyramidRight',(refractive_index_prism if TIR or refractive_index==1 else 1))
		pyrcolor=0
		if fromSurface==None:pyrcolor=0.1
		return refractionColor*(1-pyrcolor)+np.array([1,1,1])*pyrcolor
	elif Face=='pyramidLeft':
		TIR,refractedRay=refract(pyramid[0].normal,rayDirection,(1/refractive_index_prism if refractive_index!=1 else refractive_index_prism))
		refractionColor=raycast(refractedRay,point,'pyramidLeft',(refractive_index_prism if TIR or refractive_index==1 else 1))
		pyrcolor=0
		if fromSurface==None:pyrcolor=0.1
		return refractionColor*(1-pyrcolor)+np.array([1,1,1])*pyrcolor
	elif Face=='pyramidBack':
		TIR,refractedRay=refract(pyramid[2].normal,rayDirection,(1/refractive_index_prism if refractive_index!=1 else refractive_index_prism))
		refractionColor=raycast(refractedRay,point,'pyramidBack',(refractive_index_prism if TIR or refractive_index==1 else 1))
		pyrcolor=0
		if fromSurface==None:pyrcolor=0.1
		return refractionColor*(1-pyrcolor)+np.array([1,1,1])*pyrcolor
	elif Face=='pyramidBase':
		TIR,refractedRay=refract(pyramid[3].normal,rayDirection,(1/refractive_index_prism if refractive_index!=1 else refractive_index_prism))
		refractionColor=raycast(refractedRay,point+np.array([0,1e-3,0]),'pyramidBase',(refractive_index_prism if TIR or refractive_index==1 else 1))
		pyrcolor=0
		if fromSurface==None:pyrcolor=0.1
		return refractionColor*(1-pyrcolor)+np.array([1,1,1])*pyrcolor
	elif Face=='cubeTop':
		lighting=(np.dot(norm(-point+lightPosition),cube[0].normal))
		return cubeColor*(0.4+lighting*0.6)
	elif Face=='cubeFront':
		lighting=(np.dot(norm(-point+cubelightPosition),cube[1].normal))**2
		lightingspecular=(np.dot(norm(-point+lightPosition),cube[1].normal))**2
		return cubeColor*(0.4+lighting*0.5+lightingspecular*0.1)
	elif Face=='cubeSide':
		return cubeColor*0.4
	elif Face=='right_wall':
		rightWallColor=np.array([0.6,0.4,1])
		lighting=(np.dot(norm(-point+lightPosition),right_wall.normal))**3
		shadow,intersection = rayIntersect(norm(point-lightPositionShadow),lightPositionShadow,'ceiling')
		if shadow!='right_wall':
			lighting=0
		return rightWallColor*(0.4+lighting*0.6)
	elif Face=='left_wall':
		leftWallColor=np.array([1,0.6,1])
		lighting=(np.dot(norm(-point+lightPosition),left_wall.normal))**3
		return leftWallColor*(0.4+lighting*0.6)
	elif Face=='back_wall':
		backWallColor=np.array([1,0.7,0.2])
		lighting=(np.dot(norm(-point+lightPosition),back_wall.normal))**3
		return backWallColor*(0.4+lighting*0.6)
	elif Face=='ceiling':
		ceilingColor=np.array([0.7,1,0.7])
		ceilingLight=np.array([1,1,1])#pure white
		lighting=(np.dot(norm(-point+lightPosition),ceiling.normal))**0.5
		if abs(point[0])<=1 and abs(point[2])<=1:
			return ceilingLight
		return lighting
	elif Face=='floor':
		floorWhite=np.array([1,1,1])
		floorBlack=np.array([0,0,0])
		lighting=(np.dot(norm(-point+lightPosition),floor.normal))**1.5
		shadow,intersection = rayIntersect(norm(point-lightPositionShadow),lightPositionShadow,'ceiling')
		if shadow!='floor' and shadow[0]!='p':
			lighting=0
		elif shadow[0]=='p':
			lighting*=0.5
		elif shadow=='sphere':
			lighting=raycast(norm(lightPositionShadow-point),point+np.array([0,1e-3,0]),'floor',1)
		reflectedRay=rayDirection-2*np.dot(floor.normal,rayDirection)*floor.normal
		reflectionColor=raycast(reflectedRay,point,'floor',1)
		return (floorWhite if (np.floor((point[0]+3)*2)+np.floor((point[2]+3)*2))%2==1 else floorBlack)*0.3+lighting*0.4+reflectionColor*0.3
	else:
		return np.array([0.3,0.3,0.3])

right_wall.vertex[0]=[3,0,3]
right_wall.vertex[1]=[3,4,3]
right_wall.vertex[2]=[3,4,-3]
right_wall.vertex[3]=[3,0,-3]
right_wall.normal = np.array([-1,0,0])

left_wall.vertex[0]=[-3,0,3]
left_wall.vertex[1]=[-3,4,3]
left_wall.vertex[2]=[-3,4,-3]
left_wall.vertex[3]=[-3,0,-3]
left_wall.normal = np.array([1,0,0])

back_wall.vertex[0]=[3,0,-3]
back_wall.vertex[1]=[3,4,-3]
back_wall.vertex[2]=[-3,4,-3]
back_wall.vertex[3]=[-3,0,-3]
back_wall.normal = np.array([0,0,1])

ceiling.vertex[0]=[-3,4,-3]
ceiling.vertex[1]=[-3,4,3]
ceiling.vertex[2]=[3,4,3]
ceiling.vertex[3]=[3,4,-3]
ceiling.normal = np.array([0,-1,0])

floor.vertex[0]=[-3,0,-3]
floor.vertex[1]=[-3,0,3]
floor.vertex[2]=[3,0,3]
floor.vertex[3]=[3,0,-3]
floor.normal = np.array([0,1,0])

cubeCenter,cubeLength=[np.array([0.5,1,-1.5]),2**0.5]

cube[0].vertex[0]=np.array([cubeLength*np.cos(1*np.pi/4+np.pi/6),1,cubeLength*np.sin(1*np.pi/4+np.pi/6)])+cubeCenter
cube[0].vertex[1]=np.array([cubeLength*np.cos(3*np.pi/4+np.pi/6),1,cubeLength*np.sin(3*np.pi/4+np.pi/6)])+cubeCenter
cube[0].vertex[2]=np.array([cubeLength*np.cos(5*np.pi/4+np.pi/6),1,cubeLength*np.sin(5*np.pi/4+np.pi/6)])+cubeCenter
cube[0].vertex[3]=np.array([cubeLength*np.cos(7*np.pi/4+np.pi/6),1,cubeLength*np.sin(7*np.pi/4+np.pi/6)])+cubeCenter
cube[0].normal=norm(np.array([0,1,0]))

cube[1].vertex[0]=np.array([cubeLength*np.cos(1*np.pi/4+np.pi/6),1,cubeLength*np.sin(1*np.pi/4+np.pi/6)])+cubeCenter
cube[1].vertex[1]=np.array([cubeLength*np.cos(1*np.pi/4+np.pi/6),-1,cubeLength*np.sin(1*np.pi/4+np.pi/6)])+cubeCenter
cube[1].vertex[2]=np.array([cubeLength*np.cos(3*np.pi/4+np.pi/6),-1,cubeLength*np.sin(3*np.pi/4+np.pi/6)])+cubeCenter
cube[1].vertex[3]=np.array([cubeLength*np.cos(3*np.pi/4+np.pi/6),1,cubeLength*np.sin(3*np.pi/4+np.pi/6)])+cubeCenter
cube[1].normal=np.array([-np.sin(np.pi/6),0,np.cos(np.pi/6)])

cube[2].vertex[0]=np.array([cubeLength*np.cos(1*np.pi/4+np.pi/6),1,cubeLength*np.sin(1*np.pi/4+np.pi/6)])+cubeCenter
cube[2].vertex[1]=np.array([cubeLength*np.cos(1*np.pi/4+np.pi/6),-1,cubeLength*np.sin(1*np.pi/4+np.pi/6)])+cubeCenter
cube[2].vertex[2]=np.array([cubeLength*np.cos(7*np.pi/4+np.pi/6),-1,cubeLength*np.sin(7*np.pi/4+np.pi/6)])+cubeCenter
cube[2].vertex[3]=np.array([cubeLength*np.cos(7*np.pi/4+np.pi/6),1,cubeLength*np.sin(7*np.pi/4+np.pi/6)])+cubeCenter
cube[2].normal=np.array([np.cos(np.pi/6),0,np.sin(np.pi/6)])

pyramid[0].vertex[0]=np.array([-1,3,1])
pyramid[0].vertex[1]=np.array([-1,0,2])
pyramid[0].vertex[2]=np.array([-2,0,0])
pyramid[0].normal=norm(np.cross(pyramid[0].vertex[1]-pyramid[0].vertex[2],pyramid[0].vertex[0]-pyramid[0].vertex[2]))

pyramid[1].vertex[0]=np.array([-1,3,1])
pyramid[1].vertex[1]=np.array([-1,0,2])
pyramid[1].vertex[2]=np.array([0,0,0])
pyramid[1].normal=norm(-np.cross(pyramid[1].vertex[1]-pyramid[1].vertex[2],pyramid[1].vertex[0]-pyramid[1].vertex[2]))

pyramid[2].vertex[0]=np.array([-1,3,1])
pyramid[2].vertex[1]=np.array([-2,0,0])
pyramid[2].vertex[2]=np.array([0,0,0])
pyramid[2].normal=-norm(np.cross(pyramid[2].vertex[1]-pyramid[2].vertex[2],pyramid[2].vertex[0]-pyramid[2].vertex[2]))

pyramid[3].vertex[0]=np.array([-1,0,2])
pyramid[3].vertex[1]=np.array([-2,0,0])
pyramid[3].vertex[2]=np.array([0,0,0])
pyramid[3].normal=-np.array([0,1,0])

image = np.zeros((SIZEY,SIZEX,3))

eye = np.array([0,3,7])
for i in range(-SIZEX//2,SIZEX//2):
	for j in range(0,SIZEY):
		i1=i*3/(SIZEX//2)+1/(SIZEX)
		j1=j*4/SIZEY+1/(SIZEY)
		direction = norm(np.array([i1,j1,3])-eye)
		color = raycast(direction,eye,None,1)
		image[SIZEY-1-j,i+SIZEX//2]=color

plt.imshow(image)
plt.axis('off')
# plt.savefig("test.png", bbox_inches='tight',pad_inches = 0)
plt.show()